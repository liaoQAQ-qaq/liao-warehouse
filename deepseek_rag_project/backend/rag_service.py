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
        logger.info("🤖 初始化 RAG 服务 (直连强控版)...")
        
        try:
            logger.info(f"🔌 加载 Embedding: {Config.EMBEDDING_MODEL}")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=Config.EMBEDDING_MODEL,
                cache_folder=Config.MODEL_CACHE_DIR
            )
            
            logger.info(f"🧠 连接 LLM: {Config.LLM_MODEL}")
            # 🚀 关键配置：强制指定上下文窗口，防止 Empty Response
            Settings.llm = Ollama(
                model=Config.LLM_MODEL, 
                base_url=Config.LLM_API_BASE,
                request_timeout=300.0, 
                temperature=0.6,
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

        # 🚀 1. 手动检索 (Retriever) - 绕过 ChatEngine 黑盒
        logger.info(f"🔍 开始检索: {query[:20]}")
        try:
            # 只取前 3 条最相关的，避免上下文过长
            retriever = self.index.as_retriever(similarity_top_k=3)
            nodes = retriever.retrieve(query)
            # 拼接检索到的文档
            knowledge_text = "\n\n".join([f"---资料 {i+1}---\n{n.get_content()}" for i, n in enumerate(nodes)])
            if not nodes:
                knowledge_text = "（知识库中未找到直接相关内容，请依靠通用知识回答）"
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            knowledge_text = ""

        # 🚀 2. 构建消息列表 (Messages)
        chat_messages = []

        # --- A. System Message (身份核心，必须放在第一位) ---
        # 这里的指令拥有最高优先级
        system_prompt_content = (
            "你是一个专业的企业智能助手，名为“RAG企业助手”。\n"
            "【核心指令】\n"
            "1. 严禁提及“DeepSeek”、“深度求索”或你的模型版本号。\n"
            "2. 如果用户询问你是谁，必须回答：“我是您的企业智能知识库助手”。\n"
            "3. 请优先根据下方的【参考资料】和【视频分析】回答问题。\n"
            "4. 保持回答专业、客观、简洁。\n\n"
        )
        
        # 将检索到的知识和视频分析直接注入 System Prompt
        if context:
            system_prompt_content += f"【当前视频/图片分析报告】\n{context}\n\n"
        
        system_prompt_content += f"【参考资料】\n{knowledge_text}"

        chat_messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_prompt_content))

        # --- B. History Messages (历史记录) ---
        # 获取最近 4 轮对话，防止上下文溢出
        history_data = session_manager.get_messages(session_id)
        for msg in history_data[-4:]:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            if msg["content"]:
                # 过滤掉之前的思考过程标签，避免污染历史
                clean_content = msg["content"].replace("<think>", "").replace("</think>", "")
                chat_messages.append(ChatMessage(role=role, content=clean_content))

        # --- C. User Message (当前提问) ---
        chat_messages.append(ChatMessage(role=MessageRole.USER, content=query))

        try:
            print(f"🚀 [DEBUG] 向 Ollama 发送 {len(chat_messages)} 条消息...", flush=True)
            
            # 🚀 3. 直连调用 (Stream Chat)
            # 使用 Settings.llm 直接对话，不经过 LlamaIndex 的 Prompt 处理层
            response_stream = Settings.llm.stream_chat(chat_messages)
            
            has_content = False
            for chunk in response_stream:
                content = chunk.delta
                if content:
                    has_content = True
                    # 直接将原始 Token (包含 <think>) 发给前端
                    # print(content, end="", flush=True) # 调试用
                    yield content
            
            if not has_content:
                print("\n❌ [DEBUG] Ollama 返回空内容")
                yield "模型思考超时或返回为空，请重试。"

        except Exception as e:
            logger.error(f"❌ 生成出错: {e}")
            import traceback
            traceback.print_exc()
            yield f"\n[系统错误: {str(e)}]"

_rag_service = None
def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service