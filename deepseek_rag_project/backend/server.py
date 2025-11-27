import os
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
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

Config.validate()

app = FastAPI(title="DeepSeek RAG Enterprise")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    # 🚀 必须暴露自定义头，前端才能读取到 X-Session-Id
    expose_headers=["X-Session-Id"] 
)

class ChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = None

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # 1. 获取或创建 Session ID
    session_id = req.session_id
    if not session_id:
        session_id = session_manager.create_session(title=req.input[:20])
    
    session_manager.add_message(session_id, "user", req.input)

    async def response_generator():
        rag = get_rag_service()
        full_answer = ""
        try:
            # 🚀 上下文优化：获取最近的历史记录辅助检索
            # 取最近的一条 AI 回复作为背景
            history = session_manager.get_messages(session_id)
            last_ai_msg = ""
            if len(history) >= 2: # 至少有一问一答
                # 倒数第一条是刚存入的用户问题，倒数第二条是上次的AI回答
                if history[-2]['role'] == 'assistant':
                    last_ai_msg = history[-2]['content']

            # 将上下文传递给 rag_service (需要 rag_service 支持可选参数，或者简单的做法：拼接到 query)
            # 这里我们采用最稳妥的方案：仅在检索时使用拼接后的 query，但 Prompt 里还是用原始 query
            # 这一步在 rag_service 内部实现比较好，为了不改动太多，我们这里只负责传参
            # 但目前的 rag_service.chat_stream 只接受一个参数
            # 所以我们在 server 层不做拼接，保持简单，把“多轮对话能力”留给大模型自己去理解上下文
            # (LlamaIndex 的 ChatEngine 本身就有记忆，但在我们的自定义 RAG 流程中，主要靠 Prompt)
            
            async for chunk in rag.chat_stream(req.input):
                full_answer += chunk
                yield chunk
            
            clean_answer = full_answer.split("__SOURCES__")[0]
            session_manager.add_message(session_id, "assistant", clean_answer)
        except Exception as e:
            err_msg = f"Error: {str(e)}"
            yield err_msg
            session_manager.add_message(session_id, "assistant", err_msg)

    # 🚀 返回 Session ID
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