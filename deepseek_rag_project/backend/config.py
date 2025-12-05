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
print("🔧 [Config] 已强制清除系统代理配置，确保本地连接直连")

# 2. 全局强制 JSON 使用 UTF-8 编码
_original_json_dumps = json.dumps
def _force_utf8_dumps(*args, **kwargs):
    kwargs['ensure_ascii'] = False
    return _original_json_dumps(*args, **kwargs)
json.dumps = _force_utf8_dumps
print("🔧 [Config] 已开启全局 UTF-8 存储模式")

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
    
    # 🚀【核心修复】将全局变量映射到 Config 类属性中
    MODEL_CACHE_DIR = str(MODEL_CACHE_DIR)
    
    # --- 本地 DeepSeek (Ollama) 配置 ---
    LLM_API_BASE = os.getenv("LLM_API_BASE", "http://127.0.0.1:11434")
    LLM_MODEL = "deepseek-r1:7b"
    CONTEXT_WINDOW = 8192  
    
    # --- Milvus & Embedding ---
    MILVUS_URI = os.getenv("MILVUS_URI", "http://milvus-standalone:19530")
    COLLECTION_NAME = "deepseek_rag_bge_m3"
    EMBEDDING_MODEL = "/home/liaozhenhao/liao-warehouse/deepseek_rag_project/backend/model_cache/BAAI/bge-m3"
    EMBEDDING_DIM = 1024 
    
    # --- RAG 切片规则 ---
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 100

    VISION_MODEL_ID ="/home/liaozhenhao/liao-warehouse/models/Qwen2-VL-2B-Instruct"
    AUDIO_MODEL_SIZE = "large-v3"  
    # 视频抽帧间隔 (秒)
    VIDEO_FRAME_INTERVAL = 8

    # 🔥【新增配置】
    # 批处理大小：利用 32 核优势，一次并行处理 8 帧（如果内存吃紧可调小）
    VIDEO_BATCH_SIZE = 4
    # 视觉分辨率限制：取消 448 限制，提升到 1024px (约 100万像素) 以看清文字
    VIDEO_MAX_PIXELS = 768 * 768
    # 🔥【新增配置：文档与向量优化】
    # Embedding 批处理大小：每次并行计算 16 段文本的向量 (CPU 32核建议 16-32)
    # 过大可能导致延迟增加，16 是个吞吐量与延迟的平衡点
    EMBEDDING_BATCH_SIZE = 8
    
    # OCR 线程数：分配给 RapidOCR 的线程数
    OCR_THREADS = 8


    @classmethod
    def validate(cls):
        pass

# 确保目录存在
os.makedirs(Config.FILES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
os.makedirs(Config.MODEL_CACHE_DIR, exist_ok=True)