import os
from pymilvus import MilvusClient
from dotenv import load_dotenv
from pathlib import Path

# 1. 加载环境变量
current_dir = Path(__file__).parent.absolute()
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 2. 配置
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
# 这是我们要保留的、正在使用的新集合名称 (对应 vector_store.py 里的配置)
CURRENT_COLLECTION_NAME = "deepseek_rag_v2_new"

def cleanup_old_collections():
    print(f"🔌 正在连接 Milvus: {MILVUS_URI} ...")
    try:
        client = MilvusClient(uri=MILVUS_URI)
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确保 Docker 容器正在运行 (sudo docker compose ps)")
        return

    # 获取所有集合列表
    all_collections = client.list_collections()
    print(f"📦 当前数据库中发现的所有集合: {all_collections}")

    if not all_collections:
        print("✅ 数据库是空的，无需清理。")
        return

    # 遍历并删除旧集合
    deleted_count = 0
    for col_name in all_collections:
        # ⚠️ 关键逻辑：只要不是当前正在用的，统统删掉
        if col_name != CURRENT_COLLECTION_NAME:
            print(f"🗑️ 发现旧集合: [{col_name}] -> 正在删除...")
            try:
                client.drop_collection(col_name)
                print(f"   ✅ 已删除: {col_name}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ 删除失败: {e}")
        else:
            print(f"🛡️  保留当前集合: [{col_name}] (正在使用中)")

    print("-" * 30)
    if deleted_count > 0:
        print(f"🎉 清理完成！共删除了 {deleted_count} 个旧集合。")
        print("磁盘空间将由 Milvus 自动回收。")
    else:
        print("✨ 没有发现旧数据，系统非常干净！")

if __name__ == "__main__":
    # 二次确认，防止手滑
    print("⚠️  警告：此操作将删除除了 'deepseek_rag_v2_new' 以外的所有 Milvus 数据。")
    confirm = input("❓ 确认要执行吗？(输入 y 继续): ")
    
    if confirm.lower() == 'y':
        cleanup_old_collections()
    else:
        print("🚫 操作已取消")