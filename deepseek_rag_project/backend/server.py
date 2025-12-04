import os
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
# 🚀 引入 run_in_threadpool 用于解决阻塞问题
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from pymilvus import MilvusClient

from config import Config
from utils import get_file_info_list
from vector_store import get_vector_service
from rag_service import get_rag_service
from session_manager import session_manager
from video_service import get_video_service

Config.validate()

app = FastAPI(title="DeepSeek RAG Enterprise (Video Enabled)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"] 
)

class ChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = None

# 后台任务：处理永久入库的视频 (对应左侧上传)
def process_video_task(file_path: str, filename: str):
    try:
        video_svc = get_video_service()
        vector_svc = get_vector_service()
        # 这里已经是后台线程了，直接调用即可
        report = video_svc.process_video(file_path)
        vector_svc.insert_text(report, filename)
        print(f"✅ 视频 {filename} 处理并入库完成")
    except Exception as e:
        print(f"❌ 视频处理后台任务失败: {e}")

# 🚀 优化接口：使用 run_in_threadpool 防止阻塞主线程
@app.post("/api/chat/upload")
async def upload_chat_file(
    file: UploadFile = File(...), 
    session_id: str = Form(...) 
):
    try:
        file_path = os.path.join(Config.FILES_DIR, f"temp_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📂 收到临时分析视频: {file.filename}, Session: {session_id}")
        
        video_svc = get_video_service()
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            # 🚀 核心优化：将 CPU 密集的视频分析放入线程池执行
            # 这允许 FastAPI 继续处理其他请求，而不会被卡死
            report = await run_in_threadpool(video_svc.process_video, file_path)
            
            session_manager.update_session_context(session_id, report)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return {
                "message": "视频分析完成！我已经记住了内容，你可以直接提问。", 
                "report_preview": report[:100] + "..."
            }
        else:
            if os.path.exists(file_path): os.remove(file_path)
            return {"message": "目前聊天框仅支持视频文件的即时分析。"}
            
    except Exception as e:
        print(f"❌ 临时视频分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    session_id = req.session_id
    if not session_id:
        session_id = session_manager.create_session(title=req.input[:20])
    
    session_manager.add_message(session_id, "user", req.input)
    current_context = session_manager.get_session_context(session_id)

    async def response_generator():
        rag = get_rag_service()
        full_answer = ""
        try:
            # 🚀 传入 session_id，让 RAG 服务能读取历史记录
            async for chunk in rag.chat_stream(req.input, session_id, context=current_context):
                full_answer += chunk
                yield chunk
            
            clean_answer = full_answer.split("__SOURCES__")[0]
            session_manager.add_message(session_id, "assistant", clean_answer)
        except Exception as e:
            err_msg = f"Error: {str(e)}"
            yield err_msg
            session_manager.add_message(session_id, "assistant", err_msg)

    return StreamingResponse(
        response_generator(), 
        media_type="text/plain",
        headers={"X-Session-Id": session_id}
    )

@app.post("/api/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_path = os.path.join(Config.FILES_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            background_tasks.add_task(process_video_task, file_path, file.filename)
            return {"message": "视频已上传，系统正在后台进行多模态分析（耗时较长，请稍候）...", "filename": file.filename}
        else:
            vector_service = get_vector_service()
            # 文档处理也建议放到 run_in_threadpool，虽然这里用 background_tasks 也可以
            background_tasks.add_task(vector_service.process_file, file_path)
            return {"message": "上传成功，后台处理中...", "filename": file.filename}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files")
def list_files():
    return get_file_info_list(Config.FILES_DIR)

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    file_path = os.path.join(Config.FILES_DIR, filename)
    try:
        client = MilvusClient(uri=Config.MILVUS_URI)
        if client.has_collection(Config.COLLECTION_NAME):
            client.delete(
                collection_name=Config.COLLECTION_NAME,
                filter=f'file_name == "{filename}"'
            )
    except Exception as e:
        print(f"⚠️ 向量删除警告: {e}")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return {"message": "文件已删除"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
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
    uvicorn.run(app, host="0.0.0.0", port=Config.API_PORT)
