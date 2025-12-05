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
from llama_index.llms.ollama import Ollama
from pymilvus import MilvusClient
import os
import torch
import logging
import multiprocessing

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"⚙️ 初始化 LlamaIndex (高性能量化版)...")
        
        # 🚀 优化1: OCR 线程控制
        self.ocr_engine = None
        if HAS_OCR:
            try:
                # 显式限制 OCR 线程数，避免吃满所有核影响 Embedding
                logger.info(f"   👁️ 初始化 RapidOCR (Threads={Config.OCR_THREADS})...")
                self.ocr_engine = RapidOCR(num_threads=Config.OCR_THREADS)
            except Exception as e:
                logger.warning(f"RapidOCR 初始化失败: {e}")
        
        # 🚀 优化2: Embedding 模型动态量化与批处理
        logger.info(f"   🔌 加载 Embedding: {Config.EMBEDDING_MODEL}")
        logger.info(f"   ⚡ 正在应用 Embedding 动态量化 (Int8) + BatchSize={Config.EMBEDDING_BATCH_SIZE}...")
        
        # 1. 设置 Embedding 模型
        # 注意：这里我们通过 Settings 间接加载，稍后手动 hack 进行量化
        embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            cache_folder=Config.MODEL_CACHE_DIR,
            device="cpu",
            embed_batch_size=Config.EMBEDDING_BATCH_SIZE # ✅ 启用批处理
        )
        
        # 🔥【黑科技】手动对 LlamaIndex 内部的 Torch 模型进行动态量化
        try:
            # 深入获取内部的 sentence-transformers 模型
            internal_model = embed_model._model
            if hasattr(internal_model, 'encode'): # 确认是 SentenceTransformer
                # 对其内部的 auto_model (Transformer本体) 进行量化
                torch.quantization.quantize_dynamic(
                    internal_model[0].auto_model, 
                    {torch.nn.Linear}, 
                    dtype=torch.qint8,
                    inplace=True
                )
                logger.info("   ✅ Embedding 模型量化成功！(FP32 -> Int8)")
        except Exception as e:
            logger.warning(f"   ⚠️ Embedding 量化尝试失败 (将使用原精度): {e}")

        Settings.embed_model = embed_model

        # 2. 设置 LLM (DeepSeek via Ollama)
        Settings.llm = Ollama(
            model=Config.LLM_MODEL,
            base_url=Config.LLM_API_BASE,
            request_timeout=600.0
        )

        Settings.text_splitter = SentenceSplitter(
            chunk_size=Config.CHUNK_SIZE, 
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        logger.info(f"🔌 连接 Milvus: {Config.MILVUS_URI}")
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
            logger.info(f"📝 正在存入文本报告: {filename}")
            doc = Document(text=text)
            doc.metadata["file_name"] = filename
            self.index.insert(doc)
            logger.info(f"✅ 文本报告入库成功")
            return True
        except Exception as e:
            logger.error(f"❌ 文本入库失败: {e}")
            return False

    def process_file(self, filepath: str):
        try:
            logger.info(f"📄 处理文件 (高性能模式): {filepath}")
            filename = os.path.basename(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            documents = []
            
            # 图片 OCR 处理
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                if not self.ocr_engine: return False
                # RapidOCR 本身支持路径输入
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
                # 文档处理 - 利用 Embedding Batching 加速
                documents = SimpleDirectoryReader(
                    input_files=[filepath],
                    file_extractor=self.file_extractor
                ).load_data()
                for doc in documents:
                    doc.metadata["file_name"] = filename

            # 🚀 优化3: 批量插入 (Batch Insert)
            # 虽然这里是一次 insert 一个文件的所有 docs，但 index.insert 内部会触发 embedding batching
            if documents:
                logger.info(f"   ⚡ 正在向量化 {len(documents)} 个文档片段...")
                self.index.insert_nodes(
                    Settings.text_splitter.get_nodes_from_documents(documents)
                )
                
            return True
        except Exception as e:
            logger.error(f"❌ 处理失败: {e}")
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