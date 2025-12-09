from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel  # 新增导入
from typing import List         # 新增导入
from models import Base, engine, SessionLocal, Novel

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
        from_attributes = True # 兼容 SQLAlchemy 对象

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/")
async def upload_novel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text_content = content.decode("gbk")
        except:
            raise HTTPException(status_code=400, detail="Encoding not supported. Please use UTF-8.")
            
    novel = Novel(title=file.filename, content=text_content)
    db.add(novel)
    db.commit()
    db.refresh(novel)
    return {"id": novel.id, "title": novel.title}

# --- 修复：使用 response_model 自动处理 JSON 序列化 ---
@app.get("/novels/", response_model=List[NovelSchema])
def read_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 直接查询对象，Pydantic 会自动把它们转成 JSON
    novels = db.query(Novel).offset(skip).limit(limit).all()
    return novels

@app.get("/novels/{novel_id}")
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