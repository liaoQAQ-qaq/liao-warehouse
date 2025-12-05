import logging
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.milvus import MilvusVectorStore
from config import Config
from session_manager import session_manager
from prompts import build_system_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        logger.info("🤖 初始化 RAG 服务 (7B 极速版)...")
        
        try:
            logger.info(f"🔌 加载 Embedding: {Config.EMBEDDING_MODEL}")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=Config.EMBEDDING_MODEL,
                cache_folder=Config.MODEL_CACHE_DIR
            )
            
            logger.info(f"🧠 连接 LLM: {Config.LLM_MODEL}")
            # 🚀【核心优化】手动调优 Ollama 参数
            Settings.llm = Ollama(
                model=Config.LLM_MODEL, 
                base_url=Config.LLM_API_BASE,
                request_timeout=300.0, 
                temperature=0.3, 
                context_window=Config.CONTEXT_WINDOW,
                additional_kwargs={
                    "num_ctx": Config.CONTEXT_WINDOW,
                    # 🔥【关键】限制推理线程数
                    # 32核 CPU 并不意味着 num_thread=32 最快。
                    # 通常 8-16 之间是内存带宽的甜点。建议设为 12。
                    "num_thread": 12, 
                    "num_predict": -1,
                } 
            )
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            raise e

        # 移除 Reranker，追求极致响应速度
        self.reranker = None 

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

        knowledge_text = ""
        
        # 1. 上下文互斥策略 (有视频就不查文档)
        if context:
            logger.info("🎥 检测到视频上下文，跳过 RAG 检索。")
            knowledge_text = "" 
        else:
            logger.info(f"🔍 开始检索知识库: {query[:20]}")
            try:
                # 🚀【优化】只取 Top 2
                # 7B 模型阅读速度快，Top 2 (约 700 tokens) 可以在 1-2秒内读完。
                # 既保证了有足够的资料，又不会让预处理时间太长。
                retriever = self.index.as_retriever(similarity_top_k=2)
                nodes = retriever.retrieve(query)
                
                if nodes:
                    knowledge_lines = []
                    for i, n in enumerate(nodes):
                        knowledge_lines.append(f"---资料 {i+1} (仅供参考)---\n{n.get_content()}")
                    
                    if knowledge_lines:
                        knowledge_text = "\n\n".join(knowledge_lines)
                
                if not knowledge_text:
                    knowledge_text = "（未检索到高相关性文档，请忽略此部分）"
                    
            except Exception as e:
                logger.error(f"❌ 检索失败: {e}")
                knowledge_text = ""

        # 2. 构建消息
        chat_messages = []
        system_content = build_system_prompt(video_context=context, rag_context=knowledge_text)
        chat_messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_content))

        history_data = session_manager.get_messages(session_id)
        for msg in history_data[-4:]:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            if msg["content"]:
                clean_content = msg["content"].replace("<think>", "").replace("</think>", "")
                chat_messages.append(ChatMessage(role=role, content=clean_content))

        chat_messages.append(ChatMessage(role=MessageRole.USER, content=query))

        # 3. 异步流式生成
        try:
            logger.info(f"🚀 向 Ollama 发送请求 (Thread=12, Ctx={Config.CONTEXT_WINDOW})...")
            
            # 使用 astream_chat 确保非阻塞
            response_stream = await Settings.llm.astream_chat(chat_messages)
            
            has_content = False
            async for chunk in response_stream:
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