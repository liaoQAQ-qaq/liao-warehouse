import os
import json
from pathlib import Path
from dotenv import load_dotenv

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

env_path = BACKEND_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# =======================================================
# 3. 配置类
# =======================================================
class Config:
    API_PORT = int(os.getenv("API_PORT", 8000))
    FILES_DIR = str(DATA_DIR)
    DB_PATH = str(DB_PATH)
    
    # --- 本地 DeepSeek (Ollama) 配置 ---
    # 在 Docker 中访问宿主机服务需用 host.docker.internal
    LLM_API_BASE = os.getenv("LLM_API_BASE", "http://host.docker.internal:11434")
    LLM_MODEL = "deepseek-r1:14b" 
    CONTEXT_WINDOW = 8192  
    
    # --- Milvus & Embedding (修正为 BGE-M3) ---
    MILVUS_URI = os.getenv("MILVUS_URI", "http://milvus-standalone:19530")
    
    # 集合名称建议加上维度标识，防止与旧维度(512)的集合冲突
    COLLECTION_NAME = "deepseek_rag_bge_m3"
    
    # 🚀【修正】使用 BGE-M3 模型
    # 如果您已下载到本地 model_cache 目录，请保持 ./model_cache/BAAI/bge-m3
    # 如果想自动下载，可以填 "BAAI/bge-m3"
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    
    # 🚀【修正】BGE-M3 的维度是 1024 (Small 是 512)
    EMBEDDING_DIM = 1024 
    
    # 切片规则
    CHUNK_SIZE = 1024 # M3 支持长文本，可以适当调大切片
    CHUNK_OVERLAP = 100

    @classmethod
    def validate(cls):
        pass

os.makedirs(Config.FILES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)