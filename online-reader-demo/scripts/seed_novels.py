# scripts/seed_novels.py
"""
简单的种子数据脚本：
- 确保数据库已经建表
- 如果没有任何 Novel 记录，就插入几条固定数据
- 可多次执行，不会重复插
"""

import sys
from pathlib import Path

# 1. 计算项目根目录 = 当前文件所在目录的上一层
ROOT_DIR = Path(__file__).resolve().parent.parent

# 2. 把 backend 目录加到 sys.path 里，让我们可以像在 backend 里面一样 `import models`
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# 3. 现在就可以跟 backend/main.py 一样直接 from models import ...
from models import Base, engine, SessionLocal, Novel  # type: ignore[import-untyped]


def seed_novels() -> None:
    # 确保表存在
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(Novel).count()
        if count == 0:
            novels = [
                Novel(title="seed_novel_1", content="This is a seeded novel 1."),
                Novel(title="seed_novel_2", content="This is a seeded novel 2."),
            ]
            db.add_all(novels)
            db.commit()
            print("✅ Seeded 2 novels into DB.")
        else:
            print(f"✅ DB already has {count} novels, skip seeding.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_novels()
