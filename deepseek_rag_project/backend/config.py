import os
import json
from pathlib import Path
from dotenv import load_dotenv
for key in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if key in os.environ:
        del os.environ[key]
# 显式告诉程序这些地址不要走代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,milvus-standalone'

print("🔧 [Config] 已强制清除系统代理配置，确保本地连接直连")

# =======================================================
#  1. 全局强制 JSON 使用 UTF-8 编码
# =======================================================
_original_json_dumps = json.dumps

def _force_utf8_dumps(*args, **kwargs):
    kwargs['ensure_ascii'] = False
    return _original_json_dumps(*args, **kwargs)

json.dumps = _force_utf8_dumps
print("🔧 [Config] 已开启全局 UTF-8 存储模式")

# =======================================================
# 2. 环境初始化
# =======================================================
BACKEND_DIR = Path(__file__).parent.absolute()
DATA_DIR = BACKEND_DIR.parent / "data" / "files"
DB_PATH = BACKEND_DIR.parent / "data" / "sessions.db"
MODEL_CACHE_DIR = BACKEND_DIR.parent / "model_cache"  # 新增模型缓存目录

env_path = BACKEND_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# 设置 HuggingFace 镜像和缓存目录
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = str(MODEL_CACHE_DIR)

# =======================================================
# 3. 配置类
# =======================================================
class Config:
    API_PORT = int(os.getenv("API_PORT", 8000))
    FILES_DIR = str(DATA_DIR)
    DB_PATH = str(DB_PATH)
    
    # --- 本地 DeepSeek (Ollama) 配置 ---
    LLM_API_BASE = os.getenv("LLM_API_BASE", "http://127.0.0.1:11434")
    LLM_MODEL = "deepseek-r1:14b"
    CONTEXT_WINDOW = 8192  
    
    # --- Milvus & Embedding ---
    MILVUS_URI = os.getenv("MILVUS_URI", "http://milvus-standalone:19530")
    COLLECTION_NAME = "deepseek_rag_bge_m3"
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    EMBEDDING_DIM = 1024 
    
    # --- RAG 切片规则 ---
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 100


    VISION_MODEL_ID = "Qwen/Qwen2-VL-7B-Instruct"
    AUDIO_MODEL_SIZE = "large-v3"  
    # 视频抽帧间隔 (秒)
    VIDEO_FRAME_INTERVAL = 8

    @classmethod
    def validate(cls):
        pass

# 确保目录存在
os.makedirs(Config.FILES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)