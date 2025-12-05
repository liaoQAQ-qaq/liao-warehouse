import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. 代理清理
for key in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if key in os.environ:
        del os.environ[key]
# 显式告诉程序这些地址不要走代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,milvus-standalone'

# 2. 全局强制 JSON 使用 UTF-8 编码
_original_json_dumps = json.dumps
def _force_utf8_dumps(*args, **kwargs):
    kwargs['ensure_ascii'] = False
    return _original_json_dumps(*args, **kwargs)
json.dumps = _force_utf8_dumps

# 3. 路径定义 (全局变量)
BACKEND_DIR = Path(__file__).parent.absolute()
DATA_DIR = BACKEND_DIR.parent / "data" / "files"
DB_PATH = BACKEND_DIR.parent / "data" / "sessions.db"
MODEL_CACHE_DIR = BACKEND_DIR.parent / "model_cache"  

env_path = BACKEND_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# 设置 HuggingFace 镜像和缓存目录
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = str(MODEL_CACHE_DIR)

# 4. Config 类定义
class Config:
    API_PORT = int(os.getenv("API_PORT", 8000))
    FILES_DIR = str(DATA_DIR)
    DB_PATH = str(DB_PATH)
    MODEL_CACHE_DIR = str(MODEL_CACHE_DIR)
    
    # --- LLM ---
    LLM_API_BASE = os.getenv("LLM_API_BASE", "http://127.0.0.1:11434")
    LLM_MODEL = "qwen2.5:7b"
    CONTEXT_WINDOW = 4096  
    
    # --- Milvus & Embedding (Base 版配置) ---
    MILVUS_URI = os.getenv("MILVUS_URI", "http://milvus-standalone:19530")
    
    #1. 改名：使用 Base 专用集合名，避免与旧数据冲突
    COLLECTION_NAME = "rag_bge_base_v1" 
    
    #2. 换模型：使用 BGE-Base (性能与速度的黄金平衡点)
    # 如果本地没有，系统会自动从 HF 镜像下载
    EMBEDDING_MODEL = "BAAI/bge-base-zh-v1.5"
    
    EMBEDDING_DIM = 768
    
    #CPU 建议设为 32
    EMBEDDING_BATCH_SIZE = 32

    # --- Rerank ---
    RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
    
    # --- RAG 切片 ---
    CHUNK_SIZE = 512 
    CHUNK_OVERLAP = 50

    # --- 多模态 ---
    VISION_MODEL_ID ="/home/liaozhenhao/liao-warehouse/deepseek_rag_project/model_cache/models--Qwen--Qwen2-VL-7B-Instruct"
    AUDIO_MODEL_SIZE = "large-v3"  
    VIDEO_FRAME_INTERVAL = 2
    VIDEO_BATCH_SIZE = 4
    VIDEO_MAX_PIXELS = 768 * 768
    OCR_THREADS = 8

    @classmethod
    def validate(cls):
        pass

# 确保目录存在
os.makedirs(Config.FILES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
os.makedirs(Config.MODEL_CACHE_DIR, exist_ok=True)