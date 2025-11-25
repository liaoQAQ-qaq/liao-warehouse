import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 修复环境变量加载
current_dir = Path(__file__).parent.absolute()
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 2. 强制镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext, 
    Settings
)
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
import llama_index.llms.openai.utils as openai_utils
# 🚀【关键】引入 pymilvus 客户端用于执行删除操作
from pymilvus import MilvusClient 

openai_utils.ALL_AVAILABLE_MODELS["deepseek-chat"] = 64000
openai_utils.CHAT_MODELS["deepseek-chat"] = 64000

try:
    from llama_index.readers.file import FlatReader, PDFReader, DocxReader
except ImportError:
    pass

# 配置参数
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
COLLECTION_NAME = "deepseek_rag_v2_new" 
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

class VectorStoreService:
    def __init__(self):
        print("⚙️ 初始化 LlamaIndex...")
        
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-zh-v1.5",
            cache_folder="./model_cache"
        )

        Settings.llm = OpenAI(
            model="deepseek-chat",
            api_key=DEEPSEEK_API_KEY,
            api_base=DEEPSEEK_BASE_URL,
            temperature=0.3,
            max_tokens=4096,
            context_window=60000,
            is_chat_model=True
        )
        
        print(f"🔌 连接 Milvus: {MILVUS_URI}")
        # LlamaIndex 的存储接口
        self.vector_store = MilvusVectorStore(
            uri=MILVUS_URI,
            collection_name=COLLECTION_NAME,
            dim=512,
            overwrite=False
        )
        
        # 🚀【新增】独立的 Milvus 客户端，专门用于删除操作
        self.milvus_client = MilvusClient(uri=MILVUS_URI)
        
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        try:
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context
            )
            print("✅ 索引加载成功")
        except Exception:
            self.index = VectorStoreIndex.from_documents(
                [], storage_context=self.storage_context
            )

        self.file_extractor = {
            ".txt": FlatReader(),
            ".md": FlatReader(),
            ".pdf": PDFReader(),
            ".docx": DocxReader(),
            ".doc": DocxReader()
        }

    def process_file(self, filepath: str):
        try:
            print(f"📄 处理文件: {filepath}")
            documents = SimpleDirectoryReader(
                input_files=[filepath],
                file_extractor=self.file_extractor
            ).load_data()
            
            filename = os.path.basename(filepath)
            for doc in documents:
                # 记录文件名，以便删除时查找
                doc.metadata["file_name"] = filename

            for doc in documents:
                self.index.insert(doc)
                
            print(f"✅ 文件入库成功")
            return True
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False

    # 🚀【核心新增】删除文件索引的方法
    def delete_file_index(self, filename: str):
        try:
            print(f"🗑️ 正在从向量库删除: {filename}")
            # 删除所有 file_name 等于该文件的向量
            delete_expr = f'file_name == "{filename}"'
            self.milvus_client.delete(
                collection_name=COLLECTION_NAME,
                filter=delete_expr
            )
            print(f"✅ 向量数据删除成功: {filename}")
            return True
        except Exception as e:
            print(f"❌ 向量删除失败: {e}")
            return False

    def get_query_engine(self):
        return self.index.as_query_engine(similarity_top_k=4, streaming=True)

_service = None
def get_vector_service():
    global _service
    if _service is None:
        _service = VectorStoreService()
    return _service