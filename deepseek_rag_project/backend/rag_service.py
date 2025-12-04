import logging
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        logger.info("🤖 初始化 RAG 服务...")
        
        # 1. 确保 Embedding 模型加载
        if Settings.embed_model is None:
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=Config.EMBEDDING_MODEL,
                cache_folder="./model_cache"
            )
        
        # 2. 设置 LLM (DeepSeek via Ollama)
        # 保持 300s 或 600s 超时，防止 CPU 慢导致断连
        Settings.llm = Ollama(
            model=Config.LLM_MODEL, 
            base_url=Config.LLM_API_BASE,
            request_timeout=600.0,
            temperature=0.3 # 较低温度，减少幻觉
        )

        # 3. 连接 Milvus 向量库
        try:
            vector_store = MilvusVectorStore(
                uri=Config.MILVUS_URI,
                collection_name=Config.COLLECTION_NAME,
                dim=Config.EMBEDDING_DIM,
                overwrite=False
            )
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )
            logger.info("✅ RAG 索引加载成功")
        except Exception as e:
            logger.error(f"❌ RAG 初始化失败: {e}")
            self.index = None

    # 🚀 核心修改：增加 context 参数，用于接收临时视频报告
    async def chat_stream(self, query: str, context: str = ""):
        if not self.index:
            yield "系统初始化失败，无法回答。\n"
            return

        logger.info(f"🤔 收到提问: {query}")
        
        try:
            # 🚀 动态构建 System Prompt
            # 基础规则
            base_prompt = (
                "你是一个多模态视频分析助手。请根据提供的上下文信息回答问题。\n"
                "【通用规则】\n"
                "1. 区分'界面'和'剧情'：如果视觉描述包含 screenshot/interface，说明是屏幕录制，请重点描述用户操作行为，而不是复述屏幕上的文字内容。\n"
                "2. 区分'实拍'：如果视觉描述包含 dog/person/scenery，说明是实拍，请直接描述画面动作。\n"
                "3. 请用中文回答。"
            )

            # 如果存在临时上下文（刚刚在聊天框上传的视频），将其注入 Prompt 并设为最高优先级
            if context:
                logger.info("📎 检测到临时视频上下文，已注入 Prompt")
                system_prompt_str = (
                    f"{base_prompt}\n\n"
                    "【⚠️ 当前重点关注的视频/文件分析报告】：\n"
                    "--------------------------------------------------\n"
                    f"{context}\n"
                    "--------------------------------------------------\n"
                    "请优先根据上述【视频分析报告】的内容回答用户问题。\n"
                    "用户的提问（如'这个视频'、'它'）通常指代上述报告中的内容。"
                )
            else:
                # 只有 RAG 知识库的情况
                system_prompt_str = f"{base_prompt}\n请根据检索到的知识库文档回答问题。"

            # 创建聊天引擎
            chat_engine = self.index.as_chat_engine(
                chat_mode="context",
                system_prompt=system_prompt_str,
                similarity_top_k=5
            )
            
            # 开始流式生成
            response = chat_engine.stream_chat(query)
            for token in response.response_gen:
                yield token

        except Exception as e:
            logger.error(f"❌ 生成答案时出错: {e}")
            yield f"\n[系统错误: {str(e)}]"

_rag_service = None
def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service