"""
FastAPI 聊天应用服务器
支持单轮对话和多轮对话两种模式
启动命令：uvicorn fast_app:app --reload --host 0.0.0.0 --port 5000
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 用于服务静态文件
import uuid  # 用于生成唯一会话ID
import os

from chatwith_API import ChatSystem  # 导入聊天系统核心类

# 创建FastAPI应用实例
app = FastAPI(
    title="AI聊天系统",
    description="一个支持单轮和多轮对话的AI聊天系统",
    version="1.0.0"
)

# 设置静态文件目录
# 静态文件目录用于存放CSS、JavaScript等静态资源
app.mount("/static", StaticFiles(directory="static"), name="static")
# 模板文件目录
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@app.get("/{full_path:path}")
async def serve_templates(full_path: str):
    """
    服务模板文件
    """
    if not full_path:
        full_path = "index.html"
    return FileResponse(f"templates/{full_path}", media_type="text/html")

# 配置CORS（跨源资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # 只允许本地开发访问
    allow_credentials=True,  # 允许携带认证信息
    allow_methods=["GET", "POST"],  # 只允许必要的方法
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "X-Requested-With"
    ],
    expose_headers=["Content-Type", "Set-Cookie"],
    max_age=3600  # 预检请求的缓存时间
)

# 用字典存储所有用户的会话实例
# 键为会话ID，值为对应的ChatSystem实例
chat_sessions = {}

@app.get("/")
async def root():
    """
    重定向到index.html
    """
    response = RedirectResponse(url="/index.html")
    response.headers["Cache-Control"] = "no-cache"
    return response

def get_session_id(request: Request) -> str:
    """
    获取或创建会话ID
    Args:
        request: FastAPI请求对象
    Returns:
        str: 会话ID，如果不存在则创建新的
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

def get_chat_system(session_id: str) -> ChatSystem:
    """
    获取或创建聊天系统实例
    Args:
        session_id: 会话ID
    Returns:
        ChatSystem: 对应的聊天系统实例
    """
    if session_id not in chat_sessions:
        api_key = os.getenv('DEEPSEEK_API_KEY', 'your-deepseek-api-key')
        chat_sessions[session_id] = ChatSystem(api_key)
    return chat_sessions[session_id]

@app.post("/chat")
async def single_chat(request: Request):
    """
    单轮对话API端点
    每次对话都是独立的，不保存上下文
    Args:
        request: FastAPI请求对象，包含用户消息
    Returns:
        dict: 包含AI响应和对话类型的字典
    Raises:
        HTTPException: 当消息为空时抛出400错误
    """
    data = await request.json()
    user_input = data.get('message', '')
    if not user_input:
        raise HTTPException(status_code=400, detail="消息不能为空")
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    response = chat_system.single_turn_chat(user_input)
    json_response = JSONResponse(content={"response": response, "type": "single"})
    json_response.set_cookie("session_id", session_id)
    return json_response

@app.post("/multi_chat")
async def multi_chat(request: Request):
    """
    多轮对话API端点
    保持对话上下文，支持连续对话
    Args:
        request: FastAPI请求对象，包含用户消息
    Returns:
        JSONResponse: 包含AI响应和对话类型的JSON响应
    Raises:
        HTTPException: 当消息为空时抛出400错误
    """
    data = await request.json()
    user_input = data.get('message', '')
    if not user_input:
        raise HTTPException(status_code=400, detail="消息不能为空")
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    response = chat_system.multi_turn_chat(user_input)
    json_response = JSONResponse(content={"response": response, "type": "multi"})
    json_response.set_cookie("session_id", session_id)
    return json_response

@app.get("/history")
async def get_history(request: Request):
    """
    获取对话历史API端点
    返回当前会话的所有对话历史
    Args:
        request: FastAPI请求对象
    Returns:
        JSONResponse: 包含对话历史的JSON响应
    """
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    history = chat_system.get_chat_history()
    json_response = JSONResponse(content={"history": history})
    json_response.set_cookie("session_id", session_id)
    return json_response

@app.post("/clear")
async def clear_history(request: Request):
    """
    清空对话历史API端点
    清除当前会话的所有对话历史记录
    Args:
        request: FastAPI请求对象
    Returns:
        JSONResponse: 操作结果消息
    """
    session_id = get_session_id(request)
    chat_system = get_chat_system(session_id)
    chat_system.clear_history()
    json_response = JSONResponse(content={"message": "对话历史已清空"})
    json_response.set_cookie("session_id", session_id)
    return json_response

