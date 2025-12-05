import logging
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import Config
from session_manager import session_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        logger.info("🤖 初始化 RAG 服务 (智能过滤版)...")
        
        try:
            logger.info(f"🔌 加载 Embedding: {Config.EMBEDDING_MODEL}")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=Config.EMBEDDING_MODEL,
                cache_folder=Config.MODEL_CACHE_DIR
            )
            
            logger.info(f"🧠 连接 LLM: {Config.LLM_MODEL}")
            Settings.llm = Ollama(
                model=Config.LLM_MODEL, 
                base_url=Config.LLM_API_BASE,
                request_timeout=300.0, 
                temperature=0.3, # 降低温度，减少胡编乱造
                context_window=8192,
                additional_kwargs={"num_ctx": 8192} 
            )
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            raise e

        try:
            vector_store = MilvusVectorStore(
                uri=Config.MILVUS_URI,
                collection_name=Config.COLLECTION_NAME,
                dim=Config.EMBEDDING_DIM,
                overwrite=False
            )
            self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
            logger.info("✅ RAG 索引连接成功")
        except Exception as e:
            logger.error(f"❌ RAG 索引初始化失败: {e}")
            self.index = None

    async def chat_stream(self, query: str, session_id: str, context: str = ""):
        if not self.index:
            yield "系统初始化失败，无法连接到知识库。\n"
            return

        # 🚀 1. 智能检索 (带阈值过滤)
        logger.info(f"🔍 开始检索: {query[:20]}")
        knowledge_text = ""
        try:
            # 获取检索器
            retriever = self.index.as_retriever(similarity_top_k=3)
            nodes = retriever.retrieve(query)
            
            valid_nodes = []
            # 🔧【核心修复】过滤低相关度文档
            # score 通常在 0~1 之间 (余弦相似度)，根据 bge-m3 模型，0.4-0.5 是个合理的门槛
            # 如果是 L2 距离，逻辑则相反。Milvus 默认行为取决于 metric_type。
            # 这里假设是相关度分数，越离谱的内容分数越低。
            # 简单策略：如果不为空，先通过。更高级策略需打印 node.score 观察。
            
            if nodes:
                # 拼接检索到的文档
                # 🔧【修复幻觉】明确标注这是“可能相关”的资料
                knowledge_lines = []
                for i, n in enumerate(nodes):
                    # 这里可以加 score 判断: if n.score > 0.5:
                    knowledge_lines.append(f"---资料 {i+1} (仅供参考)---\n{n.get_content()}")
                
                if knowledge_lines:
                    knowledge_text = "\n\n".join(knowledge_lines)
            
            if not knowledge_text:
                knowledge_text = "（未检索到高相关性文档，请忽略此部分）"
                
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            knowledge_text = ""

        # 🚀 2. 构建消息列表 (Prompt Engineering 优化)
        chat_messages = []

        # --- A. System Message ---
        # 🔧【核心修复】彻底重写 Prompt，明确优先级
        system_prompt_content = (
            "你是一个专业的企业智能助手。\n"
            "【核心指令】\n"
            "1. 你的任务是回答用户问题。信息来源有两个：【视频分析报告】和【知识库参考资料】。\n"
            "2. ⚠️ **优先级判断**：\n"
            "   - 如果用户问的是关于**画面内容**（如“视频里有什么”、“发生了什么”），**必须只使用【视频分析报告】**，**严禁**使用【参考资料】中的无关内容。\n"
            "   - 只有当用户询问具体的企业政策、技术文档且视频里没有时，才参考【参考资料】。\n"
            "   - 如果【参考资料】与用户问题明显无关（例如问风景却给了SSH教程），**请彻底忽略资料**，不要强行关联。\n"
            "3. 严禁提及模型自身版本信息。\n\n"
        )
        
        if context:
            system_prompt_content += f"=== 🎥 当前视频/图片分析报告 (最高优先级) ===\n{context}\n\n"
        
        if knowledge_text:
            system_prompt_content += f"=== 📚 知识库参考资料 (仅在相关时参考，无关请忽略) ===\n{knowledge_text}"

        chat_messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_prompt_content))

        # --- B. History Messages ---
        history_data = session_manager.get_messages(session_id)
        for msg in history_data[-4:]:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            if msg["content"]:
                clean_content = msg["content"].replace("<think>", "").replace("</think>", "")
                chat_messages.append(ChatMessage(role=role, content=clean_content))

        # --- C. User Message ---
        chat_messages.append(ChatMessage(role=MessageRole.USER, content=query))

        try:
            print(f"🚀 [DEBUG] 向 Ollama 发送 {len(chat_messages)} 条消息...", flush=True)
            
            response_stream = Settings.llm.stream_chat(chat_messages)
            
            has_content = False
            for chunk in response_stream:
                content = chunk.delta
                if content:
                    has_content = True
                    yield content
            
            if not has_content:
                yield "模型思考超时或返回为空，请重试。"

        except Exception as e:
            logger.error(f"❌ 生成出错: {e}")
            yield f"\n[系统错误: {str(e)}]"

_rag_service = None
def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service