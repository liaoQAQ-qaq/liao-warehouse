import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 强制设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 2. 强制加载 .env
current_dir = Path(__file__).parent.absolute()
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path, override=True)

import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

from vector_store import get_vector_service
from rag_service import get_rag_service
from session_manager import session_manager

app = FastAPI(title="DeepSeek RAG System via LlamaIndex")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "../data/files"
os.makedirs(DATA_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = None

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    session_id = req.session_id
    if not session_id:
        session_id = session_manager.create_session(title=req.input[:20])
    
    session_manager.add_message(session_id, "user", req.input)

    async def response_generator():
        rag = get_rag_service()
        full_answer = ""
        try:
            # 此时 rag_service 已经是纯净版，没有来源后缀了
            async for chunk in rag.chat_stream(req.input):
                full_answer += chunk
                yield chunk
            session_manager.add_message(session_id, "assistant", full_answer)
        except Exception as e:
            err_msg = f"Error: {str(e)}"
            yield err_msg
            session_manager.add_message(session_id, "assistant", err_msg)

    return StreamingResponse(response_generator(), media_type="text/plain")

@app.post("/api/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        vector_service = get_vector_service()
        background_tasks.add_task(vector_service.process_file, file_path)
        
        return {"message": "上传成功", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/files")
def list_files():
    files = []
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            path = os.path.join(DATA_DIR, f)
            if os.path.isfile(path):
                size_kb = round(os.path.getsize(path) / 1024, 2)
                files.append({"name": f, "size": f"{size_kb} KB"})
    return files

# 🚀【核心修改】删除文件接口
@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    
    # 1. 尝试从 Milvus 数据库删除向量 (关键步骤！)
    try:
        vector_service = get_vector_service()
        vector_service.delete_file_index(filename)
    except Exception as e:
        print(f"⚠️ 数据库清理警告: {e}")

    # 2. 从本地硬盘删除文件
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return {"message": "文件及索引已删除"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
            
    raise HTTPException(status_code=404, detail="文件不存在")

@app.get("/api/sessions")
def list_sessions():
    return session_manager.get_sessions()

@app.get("/api/sessions/{session_id}/messages")
def get_session_history(session_id: str):
    return session_manager.get_messages(session_id)

@app.delete("/api/sessions/{session_id}")
def delete_session_endpoint(session_id: str):
    try:
        session_manager.delete_session(session_id)
        return {"message": "会话已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)