from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from .models import Base, engine, SessionLocal, Novel

# SQLite 能支持的最大有符号整数（理论上可以不限制到这么大，你也可以自己降到 2**31-1）
MAX_SQLITE_INT = 9223372036854775807  # 2**63 - 1

# 初始化数据库
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic 模型：对外返回结构 ---


class NovelSchema(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True  # 兼容 SQLAlchemy 对象


class NovelDetailSchema(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class DeleteResponseSchema(BaseModel):
    detail: str


# --- DB Session 依赖 ---


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 接口实现 ---


@app.post("/upload/")
async def upload_novel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()

    # 宽松版：尽量不抛 400，只是按顺序尝试多种编码
    text_content = None
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            text_content = content.decode(encoding)
            break
        except UnicodeDecodeError:
            text_content = None

    if text_content is None:
        # 理论上很难走到这里，但真的全都失败就用 repr(二进制) 兜底
        text_content = repr(content)

    novel = Novel(title=file.filename, content=text_content)
    db.add(novel)
    db.commit()
    db.refresh(novel)
    return {"id": novel.id, "title": novel.title}


@app.get("/novels/", response_model=List[NovelSchema])
def read_novels(
    skip: int = Query(0, ge=0, le=100000),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    novels = db.query(Novel).offset(skip).limit(limit).all()
    return novels


@app.get("/novels/{novel_id}", response_model=NovelDetailSchema)
def get_novel(
    novel_id: int = Path(
        ...,
        description="Novel ID (positive integer within supported range)",
        ge=1,
        le=MAX_SQLITE_INT,
    ),
    db: Session = Depends(get_db),
):
    # 这里不再自己做 422 校验，交给 FastAPI 的 Path 约束生成 HTTPValidationError
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel


@app.delete("/novels/{novel_id}", response_model=DeleteResponseSchema)
def delete_novel(
    novel_id: int = Path(
        ...,
        description="Novel ID (positive integer within supported range)",
        ge=1,
        le=MAX_SQLITE_INT,
    ),
    db: Session = Depends(get_db),
):
    # 同样参数范围校验交给 Path
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    db.delete(novel)
    db.commit()
    return {"detail": "Deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    # 本地开发手动跑：
    #   cd backend && python main.py
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
