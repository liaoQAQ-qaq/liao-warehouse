from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

try:
    # 情况1：本地 / CI 里，import backend.main 时走这里
    from .models import Base, engine, SessionLocal, Novel  # type: ignore[import]
except ImportError:
    # 情况2：Docker 里以 "main" 顶层模块运行时走这里
    from models import Base, engine, SessionLocal, Novel

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
    """上传小说文本文件。

    约定：
    - 只接受 UTF-8 编码的文本文件
    - 解码失败视为无效请求，返回 422 + 标准 ValidationError 结构
    """
    content = await file.read()

    # 只接受 UTF-8 文本；解码失败则视为“无效输入”
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        # 注意：detail 要做成 FastAPI 默认的 ValidationError 结构，
        # 这样才符合 openapi.yaml 里 HTTPValidationError 的 schema
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "file"],
                    "msg": "Uploaded file must be a UTF-8 encoded text file.",
                    "type": "value_error.binary.invalid_encoding",
                }
            ],
        )

    # 额外兜底：空文件也算无效
    if not text_content.strip():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "file"],
                    "msg": "Uploaded file is empty.",
                    "type": "value_error.binary.empty",
                }
            ],
        )

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

