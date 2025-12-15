from fastapi import FastAPI, Query, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel  # 新增导入
from typing import List  # 新增导入
from .models import Base, engine, SessionLocal, Novel



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


# --- 新增：定义返回给前端的数据模型 (Pydantic) ---
class NovelSchema(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True  # 兼容 SQLAlchemy 对象


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload/")
async def upload_novel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    # 宽松版：尽量不抛 400，只是按顺序尝试多种编码
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


# --- 修复：使用 response_model 自动处理 JSON 序列化 ---
@app.get("/novels/", response_model=List[NovelSchema])
def read_novels(
    skip: int = Query(0, ge=0, le=100000),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    novels = db.query(Novel).offset(skip).limit(limit).all()
    return novels


class NovelDetailSchema(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


@app.get("/novels/{novel_id}", response_model=NovelDetailSchema)
def read_novel(novel_id: int, db: Session = Depends(get_db)):
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel


@app.delete("/novels/{novel_id}")
def delete_novel(novel_id: int, db: Session = Depends(get_db)):
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        raise HTTPException(status_code=404, detail="Novel not found")

    db.delete(novel)
    db.commit()
    return {"detail": "Deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    # 第一个参数是字符串格式的 "文件名:实例名"
    # reload=True 表示代码修改后自动重启 (开发模式)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
