from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RAGC import RAGChain
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


import os

app = FastAPI()

# 定义请求模型
class QuestionRequest(BaseModel):
    question: str

# 初始化 RAGChain
base_dir = os.path.join(os.path.dirname(__file__), "documents")
embedding_model_path = r"E:\0projects\summer_school\embedding_models\moka\m3e-base"

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

rag_chain = RAGChain(base_dir, embedding_model_path, api_key)
rag_chain.load_documents()
embedding_model = rag_chain.initialize_embedding_model()
rag_chain.create_vectorstore(embedding_model)
rag_chain.initialize_chat_model()
rag_chain.create_qa_chain()

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        result = rag_chain.ask_question(request.question)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
