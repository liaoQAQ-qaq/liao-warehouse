import os
import shutil

# 1. 强制配置国内镜像（确保速度）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import snapshot_download
from pathlib import Path

# 2. 精确定位缓存目录
BACKEND_DIR = Path(__file__).parent.absolute()
MODEL_CACHE_DIR = BACKEND_DIR.parent / "model_cache"

print(f"📍 锁定模型缓存目录: {MODEL_CACHE_DIR}")

def force_clean_and_download(repo_id):
    # 构造该模型在本地的具体路径名称
    # HuggingFace 缓存文件夹命名规则: models--作者--模型名
    dir_name = f"models--{repo_id.replace('/', '--')}"
    target_dir = MODEL_CACHE_DIR / dir_name

    print(f"\n==================================================")
    print(f"🛠️  正在处理: {repo_id}")
    
    # 3. 强制删除旧缓存 (物理粉碎)
    if target_dir.exists():
        print(f"⚠️  发现残留缓存，正在强制删除: {target_dir}")
        try:
            shutil.rmtree(target_dir)
            print("✅ 旧缓存已彻底清除")
        except Exception as e:
            print(f"❌ 删除失败 (请尝试用 sudo 运行或手动删除): {e}")
            return
    else:
        print("ℹ️  未发现残留目录，准备全新下载")

    # 4. 重新下载
    print(f"⬇️  开始下载 (多线程加速中)...")
    try:
        path = snapshot_download(
            repo_id=repo_id,
            cache_dir=MODEL_CACHE_DIR,
            resume_download=True,  # 允许断点续传（这次是干净的目录，不会错乱）
            max_workers=8,         # 8线程并发
            # 忽略不必要的权重文件，只下载 safetensors，节省时间和空间
            ignore_patterns=["*.DS_Store", "*.msgpack", "*.h5", "*.bin", "*.pth"] 
        )
        print(f"✅ 下载成功: {path}")
    except Exception as e:
        print(f"❌ 下载失败: {e}")

if __name__ == "__main__":
    # 1. 重置 Qwen2-VL-7B (视觉)
    force_clean_and_download("Qwen/Qwen2-VL-7B-Instruct")
    
    # 2. 重置 Faster-Whisper Large-v3 (听觉)
    force_clean_and_download("Systran/faster-whisper-large-v3")
    
    print("\n🎉 所有模型已重置并下载完毕！请重新运行 python server.py")