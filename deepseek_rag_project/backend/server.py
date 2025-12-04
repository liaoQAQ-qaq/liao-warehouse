import os
import shutil
# 🚀 引入 Form，用于接收表单数据
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
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
        
        # 1. 生成分析报告
        report = video_svc.process_video(file_path)
        
        # 2. 将报告存入向量库
        vector_svc.insert_text(report, filename)
        print(f"✅ 视频 {filename} 处理并入库完成")
    except Exception as e:
        print(f"❌ 视频处理后台任务失败: {e}")

# 🚀 新增接口：处理聊天框上传的临时视频 (只分析，不入库)
@app.post("/api/chat/upload")
async def upload_chat_file(
    file: UploadFile = File(...), 
    session_id: str = Form(...) # 接收 session_id
):
    try:
        # 1. 保存临时文件
        file_path = os.path.join(Config.FILES_DIR, f"temp_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📂 收到临时分析视频: {file.filename}, Session: {session_id}")

        # 2. 调用视频服务进行分析
        video_svc = get_video_service()
        
        # 简单判断是否为视频
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            # 注意：这里是同步等待分析完成，为了让前端能显示"分析完成"
            # 如果视频非常长，这里可能会耗时较久，建议上传短视频
            report = video_svc.process_video(file_path)
            
            # 3. 关键步骤：将报告存入 Session 上下文，而不是 Milvus
            # (前提：你已经在 session_manager.py 中添加了 update_session_context 方法)
            session_manager.update_session_context(session_id, report)
            
            # 4. 清理临时文件
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

    # 🚀 获取当前 Session 的临时上下文 (如果有刚刚上传的视频报告)
    # (前提：你已经在 session_manager.py 中添加了 get_session_context 方法)
    current_context = session_manager.get_session_context(session_id)

    async def response_generator():
        rag = get_rag_service()
        full_answer = ""
        try:
            # 🚀 将 context 传入 chat_stream
            async for chunk in rag.chat_stream(req.input, context=current_context):
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
    # 左侧侧边栏的“永久入库”上传逻辑
    try:
        file_path = os.path.join(Config.FILES_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            # 视频：后台异步处理
            background_tasks.add_task(process_video_task, file_path, file.filename)
            return {"message": "视频已上传，系统正在后台进行多模态分析（耗时较长，请稍候）...", "filename": file.filename}
        else:
            # 文档：后台异步处理
            vector_service = get_vector_service()
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