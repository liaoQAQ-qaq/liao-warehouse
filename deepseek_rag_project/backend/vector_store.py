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

# 1. 注册 DeepSeek
openai_utils.ALL_AVAILABLE_MODELS[Config.LLM_MODEL] = Config.CONTEXT_WINDOW
openai_utils.CHAT_MODELS[Config.LLM_MODEL] = Config.CONTEXT_WINDOW

# 2. 尝试导入 RapidOCR (替换原有的 PaddleOCR)
try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("⚠️ 未检测到 rapidocr_onnxruntime，图片功能将禁用。")

try:
    from llama_index.readers.file import FlatReader, PDFReader, DocxReader
except ImportError:
    pass

class VectorStoreService:
    def __init__(self):
        print(f"⚙️ 初始化 LlamaIndex (模型: {Config.EMBEDDING_MODEL})...")
        
        # 3. 初始化 RapidOCR
        self.ocr_engine = None
        if HAS_OCR:
            try:
                print("👁️ 初始化 RapidOCR...")
                self.ocr_engine = RapidOCR()
                print("✅ RapidOCR 初始化成功")
            except Exception as e:
                print(f"❌ RapidOCR 初始化失败: {e}")
        
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
                
                print("👁️ 正在进行 OCR 识别 (RapidOCR)...")
                
                # RapidOCR 调用方式
                result, _ = self.ocr_engine(filepath)
                
                ocr_text = ""
                # 处理返回结果: RapidOCR 返回 [[box], text, score]
                if result:
                    for line in result:
                        if line and len(line) >= 2:
                            text = line[1]
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
                    input_files=[filepath], #加载指定文件
                    file_extractor=self.file_extractor #使用对应的文件读取器解析对应格式文件
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