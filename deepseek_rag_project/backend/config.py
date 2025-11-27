import os
import json
from pathlib import Path
from dotenv import load_dotenv

# =======================================================
# 🚀 1. 全局强制 JSON 使用 UTF-8 编码
# 解决 Attu 中查看中文乱码的问题
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
    
    # DeepSeek
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    LLM_MODEL = "deepseek-chat"
    CONTEXT_WINDOW = 64000
    
    # Milvus & BGE-M3
    MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
    COLLECTION_NAME = "deepseek_rag_bge_m3"
    
    # 这里的路径假设你已经运行 download_model.py 下载好了
    EMBEDDING_MODEL = "./model_cache/BAAI/bge-m3"
    EMBEDDING_DIM = 1024 # BGE-M3 的维度
    
    # 切片规则
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 100

    @classmethod
    def validate(cls):
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("❌ 错误: 未找到 DEEPSEEK_API_KEY，请检查 .env 文件！")

os.makedirs(Config.FILES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)