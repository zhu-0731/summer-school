from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os

from chatwith_API import ChatSystem

app = FastAPI()

# 允许跨域（如有前端页面需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储用户会话
chat_sessions = {}

def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

def get_chat_system(session_id: str):
    if session_id not in chat_sessions:
        api_key = os.getenv('DEEPSEEK_API_KEY', 'your-deepseek-api-key')
        chat_sessions[session_id] = ChatSystem(api_key)
    return chat_sessions[session_id]

@app.post("/api/single_chat")
async def single_chat(request: Request):
    data = await request.json()
    user_input = data.get('message', '')
    if not user_input:
        raise HTTPException(status_code=400, detail="消息不能为空")
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    response = chat_system.single_turn_chat(user_input)
    return {"response": response, "type": "single"}

@app.post("/api/multi_chat")
async def multi_chat(request: Request):
    data = await request.json()
    user_input = data.get('message', '')
    if not user_input:
        raise HTTPException(status_code=400, detail="消息不能为空")
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    response = chat_system.multi_turn_chat(user_input)
    return {"response": response, "type": "multi"}

@app.get("/api/history")
async def get_history(request: Request):
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    history = chat_system.get_chat_history()
    return {"history": history}

@app.post("/api/clear")
async def clear_history(request: Request):
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    chat_system.clear_history()
    return {"message": "对话历史已清空"}

# 启动命令（终端运行）
# uvicorn 你的文件名:app --reload --host 0.0.0.0 --port 5000