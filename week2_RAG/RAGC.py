import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain.chains import RetrievalQA
from langchain.retrievers import MultiQueryRetriever
from pydantic import SecretStr



class RAGChain:
    def __init__(self, base_dir, embedding_model_path, api_key):
        self.base_dir = base_dir
        self.embedding_model_path = embedding_model_path
        self.api_key = api_key
        self.documents = []
        self.vectorstore = None
        self.chat_model = None
        self.qa_chain = None
        

    def load_documents(self):
        if not os.path.exists(self.base_dir):
            print(f"目录 '{self.base_dir}' 不存在，正在创建...")
            os.makedirs(self.base_dir)

        for file in os.listdir(self.base_dir):
            file_path = os.path.join(self.base_dir, file)
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                self.documents.extend(loader.load())
            elif file.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
                self.documents.extend(loader.load())
            elif file.endswith(".txt"):
                with open(file_path, encoding="utf-8") as f:
                    text = f.read()
                self.documents.append({"content": text, "file_path": file_path})

        print(f"Loaded {len(self.documents)} documents from {self.base_dir}")

    def initialize_embedding_model(self):
        if not os.path.exists(self.embedding_model_path):
            raise FileNotFoundError(f"模型路径 {self.embedding_model_path} 不存在，请检查路径或下载模型")

        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}

        embedding_model = HuggingFaceEmbeddings(
            model_name=self.embedding_model_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        return embedding_model

    def create_vectorstore(self, embedding_model):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        documents = [
            Document(page_content=doc["content"], metadata={"file_path": doc["file_path"]})
            for doc in self.documents
        ]
        chunked_documents = text_splitter.split_documents(documents)

        self.vectorstore = Qdrant.from_documents(
            documents=chunked_documents,
            embedding=embedding_model,
            location=":memory:",
            collection_name="my_documents"
        )

    def initialize_chat_model(self):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")

        self.chat_model = ChatDeepSeek(
            model="deepseek-chat",
            api_key=SecretStr(self.api_key)
        )

    def create_qa_chain(self):
        if not self.vectorstore:
            raise ValueError("Vectorstore 未初始化，请先调用 create_vectorstore 方法。")
        if not self.chat_model:
            raise ValueError("Chat model 未初始化，请先调用 initialize_chat_model 方法。")

        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=self.vectorstore.as_retriever(),
            llm=self.chat_model
        )

        self.qa_chain = RetrievalQA.from_chain_type(self.chat_model, retriever=retriever_from_llm)

    def ask_question(self, question):
        if not self.qa_chain:
            raise ValueError("QA Chain 未初始化")

        result = self.qa_chain.invoke({"query": question})
        return result
