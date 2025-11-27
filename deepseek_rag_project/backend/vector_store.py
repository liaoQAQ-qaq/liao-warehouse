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
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from pymilvus import MilvusClient
import llama_index.llms.openai.utils as openai_utils
import os
import logging

# 屏蔽 PaddleOCR 的调试日志
logging.getLogger("ppocr").setLevel(logging.WARNING)

# 1. 注册 DeepSeek
openai_utils.ALL_AVAILABLE_MODELS[Config.LLM_MODEL] = Config.CONTEXT_WINDOW
openai_utils.CHAT_MODELS[Config.LLM_MODEL] = Config.CONTEXT_WINDOW

# 2. 尝试导入 PaddleOCR
try:
    from paddleocr import PaddleOCR
    HAS_PADDLE = True
except ImportError:
    HAS_PADDLE = False
    print("⚠️ 未检测到 paddleocr，图片功能将禁用。")

try:
    from llama_index.readers.file import FlatReader, PDFReader, DocxReader
except ImportError:
    pass

class VectorStoreService:
    def __init__(self):
        print(f"⚙️ 初始化 LlamaIndex (模型: {Config.EMBEDDING_MODEL})...")
        
        # 3. 初始化 PaddleOCR
        self.ocr_engine = None
        if HAS_PADDLE:
            try:
                print("👁️ 初始化 PaddleOCR (中文模式)...")
                # 🚀【初始化】只使用最基础、最稳健的参数
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=True, # 开启方向检测
                    lang="ch"           # 中文模式
                )
                print("✅ PaddleOCR 初始化成功")
            except Exception as e:
                print(f"❌ PaddleOCR 初始化尝试失败: {e}")
                # 绝地求生模式：什么参数都不传，只求能跑
                try:
                    print("⚠️ 尝试无参数初始化...")
                    self.ocr_engine = PaddleOCR(lang="ch")
                    print("✅ PaddleOCR 降级初始化成功")
                except:
                    print("❌ OCR 彻底不可用")
        
        # 4. Embedding
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            cache_folder="./model_cache"
        )

        # 5. LLM
        Settings.llm = OpenAI(
            model=Config.LLM_MODEL,
            api_key=Config.DEEPSEEK_API_KEY,
            api_base=Config.DEEPSEEK_BASE_URL,
            temperature=0.3,
            max_tokens=4096,
            context_window=Config.CONTEXT_WINDOW,
            is_chat_model=True
        )

        # 6. 切片
        Settings.text_splitter = SentenceSplitter(
            chunk_size=Config.CHUNK_SIZE, 
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        print(f"🔌 连接 Milvus: {Config.MILVUS_URI}")
        
        # 7. Milvus
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
            print(f"✅ 成功加载向量集合: {Config.COLLECTION_NAME}")
        except Exception:
            print("ℹ️ 初始化新索引")
            self.index = VectorStoreIndex.from_documents([], storage_context=self.storage_context)

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
            filename = os.path.basename(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            
            documents = []

            # 🚀 图片处理分支
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                if not self.ocr_engine:
                    print("❌ OCR 引擎未启动，无法识别图片")
                    return False
                
                print("👁️ 正在进行深度 OCR 识别 (PaddleOCR)...")
                
                # 🚀【关键修复】直接调用，不传 cls=True
                # 因为初始化时已经指定了 use_angle_cls=True，这里不需要再传
                result = self.ocr_engine.ocr(filepath)
                
                ocr_text = ""
                # 处理返回结果
                if result and result[0]:
                    for line in result[0]:
                        if line and len(line) > 1:
                            text = line[1][0]
                            ocr_text += text + "\n"
                
                print(f"📝 识别结果预览: {ocr_text[:100].replace(chr(10), ' ')}...")
                
                if not ocr_text.strip():
                    print("⚠️ OCR 未识别到有效文字")
                    return False

                doc = Document(text=ocr_text)
                doc.metadata["file_name"] = filename
                documents = [doc]

            else:
                # 普通文件
                documents = SimpleDirectoryReader(
                    input_files=[filepath],
                    file_extractor=self.file_extractor
                ).load_data()
                
                for doc in documents:
                    doc.metadata["file_name"] = filename

            # 入库
            for doc in documents:
                self.index.insert(doc)
                
            print(f"✅ 文件入库成功 (BGE-M3)")
            return True

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
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

    def get_query_engine(self):
        return self.index.as_query_engine(similarity_top_k=4, streaming=True)

_service = None
def get_vector_service():
    global _service
    if _service is None:
        _service = VectorStoreService()
    return _service