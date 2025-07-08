import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv
load_dotenv()

# 使用绝对路径定义文档目录
base_dir = os.path.join(os.path.dirname(__file__), "documents")
documents = []

# 检查目录是否存在，如果不存在则创建
if not os.path.exists(base_dir):
    print(f"目录 '{base_dir}' 不存在，正在创建...")
    os.makedirs(base_dir)

# 遍历目录中的文件，根据文件类型加载内容
for file in os.listdir(base_dir):
    file_path = os.path.join(base_dir, file)
    if file.endswith(".pdf"):
        # 加载 PDF 文件
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith(".docx"):
        # 加载 DOCX 文件
        loader = Docx2txtLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith(".txt"):
        # 加载 TXT 文件，显式指定编码为 utf-8
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        documents.append({"content": text, "file_path": file_path})

# 打印加载的文档数量和内容
print(f"Loaded {len(documents)} documents from {base_dir}")
print("Documents:", documents)

from langchain.text_splitter import RecursiveCharacterTextSplitter

# 初始化文本分割器，设置分割块大小和重叠
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)

# 定义嵌入模型路径
m3e_name = r"E:\0projects\summer_school\embedding_models\moka\m3e-base"
bce_name = r"E:\0projects\summer_school\embedding_models\netease-youdao\bce-embedding-base_v1"

# 设置模型参数，使用 CPU 设备
model_kwargs={"device": "cpu"}  # 使用 CPU 设备

# 编码时完成归一化
encode_kwargs = {'normalize_embeddings': True}

# 导入 HuggingFace 嵌入模型
from langchain_huggingface import HuggingFaceEmbeddings

# 检查模型路径是否存在
if not os.path.exists(m3e_name):
    raise FileNotFoundError(f"模型路径 {m3e_name} 不存在，请检查路径或下载模型")


# 初始化 HuggingFace 嵌入模型
embedding_model = HuggingFaceEmbeddings(
    model_name=m3e_name,  # 模型名称
    model_kwargs=model_kwargs,  # 模型参数
    encode_kwargs=encode_kwargs  # 编码参数
)

#pip install qdrant-client

from langchain_community.vectorstores import Qdrant

# 将字典转换为具有 page_content 属性的对象
from langchain.schema import Document

documents = [
    Document(page_content=doc["content"], metadata={"file_path": doc["file_path"]})
    for doc in documents
]

# 定义 chunked_documents
chunked_documents = text_splitter.split_documents(documents)

# 使用 Qdrant 创建向量存储，存储在内存中
# 修正路径格式为原始字符串，避免误解为 URL
vectorstore = Qdrant.from_documents(
    documents=chunked_documents,  # 分割后的文档
    embedding=embedding_model,  # 嵌入模型
    location=":memory:",  # 使用内存模式
    collection_name="my_documents"  # 集合名称
)


from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

# api_key_value = os.getenv("DEEPSEEK_API_KEY")
# if not api_key_value:
#     raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
# chat_model = ChatOpenAI(
#     model="gpt-4o-mini",  # 使用 GPT-4o-mini 模型
#     api_key=SecretStr(api_key_value),  # 替换为你的 API 密钥
# )
api_key_value = os.getenv("DEEPSEEK_API_KEY")

print(f"Loaded API Key: {os.getenv('DEEPSEEK_API_KEY')}")

if not api_key_value:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")

chat_model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=SecretStr(api_key_value),  # 使用 SecretStr 包装 API 密钥
    )

# 修正导入路径
from langchain.chains import RetrievalQA
from langchain.retrievers import MultiQueryRetriever

retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),  # 使用向量存储的检索器
    llm=chat_model,  # 使用聊天模型
)

qa_chain = RetrievalQA.from_chain_type(chat_model, retriever=retriever_from_llm)



question = "理想是"
result = qa_chain.invoke({"query": question})
print(result)