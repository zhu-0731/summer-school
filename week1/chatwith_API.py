# requirements.txt
"""
langchain==0.1.0
langchain-openai==0.0.5
flask==2.3.3
python-dotenv==1.0.0
"""

# chat_system.py
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain.llms.base import LLM
from langchain.schema import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage
)
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import requests
import json

# 加载环境变量
load_dotenv()

class DeepSeekLLM(LLM):
    """自定义DeepSeek LLM包装器"""
    
    api_key: str
    api_base: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 1024

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, api_key: str):  # 删除 **kwargs，直接只接收 api_key
        """初始化 DeepSeek LLM"""

        # 先调用父类的初始化
        # super().__init__(
        #     api_key=api_key,
        #     api_base="https://api.deepseek.com/v1",
        #     model_name="deepseek-chat",
        #     temperature=0.7,
        #     max_tokens=1024
        # )

        # 创建基类所需的所有参数字典
        kwargs = {
            "api_key": api_key,
            "api_base": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 1024
        }
        # 调用父类初始化
        super().__init__(**kwargs)
    
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            return f"API调用错误: {str(e)}"

class ChatSystem:
    """对话系统主类"""
    
    def __init__(self, api_key: str, use_ollama: bool = True):
        """
        初始化聊天系统
        Args:
            api_key: API密钥（用于DeepSeek模式）
            use_ollama: 是否使用Ollama模式，默认False使用DeepSeek模式
        """
        if use_ollama:
            # 使用Ollama模式
            from langchain_community.chat_models import ChatOllama
            self.llm = ChatOllama(
                base_url="https://2a0b-2001-250-401-6601-d52e-2189-d785-cf66.ngrok-free.app",
                model="deepseek-r1:14b",
                temperature=0.7,
            )
        else:
            # 使用DeepSeek模式
            self.llm = DeepSeekLLM(api_key=api_key)
        
        # 创建对话模板
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template="""你是一个有用的AI助手。
            请根据对话历史和用户当前的问题，给出准确、有帮助的回答。
            对话历史:
            {history}
            用户: {input}
            助手: """
        )
        
        # 初始化记忆
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # 创建对话链
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory,
            verbose=True
        )
        
        # 存储对话历史
        self.chat_history: List[Dict[str, str]] = []
    
    def single_turn_chat(self, user_input: str) -> str:
        """单轮对话 - 不保存历史记录"""
        try:
            if isinstance(self.llm, DeepSeekLLM):
                # DeepSeek模式直接返回字符串
                return self.llm._call(user_input)
            else:
                # 对于 ChatOllama，使用标准的消息格式
                messages = [
                    SystemMessage(content="你是一个有帮助的AI助手。"),
                    HumanMessage(content=user_input)
                ]
                ai_message = self.llm(messages)  # 返回 AIMessage 对象
                return str(ai_message.content)  # 确保返回字符串
        except Exception as e:
            return f"单轮对话出错: {str(e)}"
    
    def multi_turn_chat(self, user_input: str) -> str:
        """多轮对话 - 保存历史记录"""
        try:
            # 使用conversation chain进行多轮对话
            response = self.conversation.predict(input=user_input)
            
            # 保存到历史记录
            self.chat_history.append({
                "user": user_input,
                "assistant": response,
                "timestamp": self._get_timestamp()
            })
            
            return response
        except Exception as e:
            return f"多轮对话出错: {str(e)}"
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.chat_history
    
    def clear_history(self):
        """清空对话历史"""
        self.memory.clear()
        self.chat_history.clear()
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

