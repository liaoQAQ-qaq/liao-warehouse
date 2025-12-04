from config import Config
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext, 
    Settings,
    Document
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.milvus import MilvusVectorStore
# 🚀 修正引用：使用 huggingface 插件包
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# 🚀 修正引用：使用 ollama 插件包
from llama_index.llms.ollama import Ollama
from pymilvus import MilvusClient
import os

# 尝试导入 RapidOCR
try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    from llama_index.readers.file import FlatReader, PDFReader, DocxReader
except ImportError:
    pass

class VectorStoreService:
    def __init__(self):
        print(f"⚙️ 初始化 LlamaIndex (Embedding: {Config.EMBEDDING_MODEL})...")
        
        self.ocr_engine = None
        if HAS_OCR:
            try:
                self.ocr_engine = RapidOCR()
            except Exception:
                pass
        
        # 1. 设置 Embedding
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            cache_folder="./model_cache"
        )

        # 2. 设置 LLM (DeepSeek via Ollama)
        Settings.llm = Ollama(
            model=Config.LLM_MODEL, # 使用 config 中的 deepseek-r1:14b
            base_url=Config.LLM_API_BASE,
            request_timeout=600.0
        )

        Settings.text_splitter = SentenceSplitter(
            chunk_size=Config.CHUNK_SIZE, 
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        print(f"🔌 连接 Milvus: {Config.MILVUS_URI}")
        self.vector_store = MilvusVectorStore(
            uri=Config.MILVUS_URI,
            collection_name=Config.COLLECTION_NAME,
            dim=Config.EMBEDDING_DIM,
            overwrite=False
        )
        
        self.milvus_client = MilvusClient(uri=Config.MILVUS_URI)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        try:
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context
            )
        except Exception:
            self.index = VectorStoreIndex.from_documents([], storage_context=self.storage_context)

        self.file_extractor = {
            ".txt": FlatReader(),
            ".md": FlatReader(),
            ".pdf": PDFReader(),
            ".docx": DocxReader(),
            ".doc": DocxReader()
        }

    def insert_text(self, text: str, filename: str):
        """直接存入文本报告"""
        try:
            print(f"📝 正在存入文本报告: {filename}")
            doc = Document(text=text)
            doc.metadata["file_name"] = filename
            self.index.insert(doc)
            print(f"✅ 文本报告入库成功")
            return True
        except Exception as e:
            print(f"❌ 文本入库失败: {e}")
            return False

    def process_file(self, filepath: str):
        try:
            print(f"📄 处理文件: {filepath}")
            filename = os.path.basename(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            documents = []
            
            # 图片 OCR 处理
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                if not self.ocr_engine: return False
                result, _ = self.ocr_engine(filepath)
                ocr_text = ""
                if result:
                    for line in result:
                        if line and len(line) >= 2: ocr_text += line[1] + "\n"
                if not ocr_text.strip(): return False
                doc = Document(text=ocr_text)
                doc.metadata["file_name"] = filename
                documents = [doc]
            else:
                # 文档处理
                documents = SimpleDirectoryReader(
                    input_files=[filepath],
                    file_extractor=self.file_extractor
                ).load_data()
                for doc in documents:
                    doc.metadata["file_name"] = filename

            for doc in documents:
                self.index.insert(doc)
            return True
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False

    def delete_file_index(self, filename: str):
        try:
            self.milvus_client.delete(
                collection_name=Config.COLLECTION_NAME,
                filter=f'file_name == "{filename}"'
            )
            return True
        except Exception:
            return False

_service = None
def get_vector_service():
    global _service
    if _service is None:
        _service = VectorStoreService()
    return _service