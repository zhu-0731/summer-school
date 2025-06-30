# requirements.txt
"""
langchain==0.1.0
langchain-openai==0.0.5
flask==2.3.3
python-dotenv==1.0.0
"""

# chat_system.py
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.llms.base import LLM
from langchain.schema import BaseMessage, HumanMessage, AIMessage
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
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(self, prompt: str, stop: List[str] = None) -> str:
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
    
    def __init__(self, api_key: str):
        # 初始化DeepSeek LLM
        self.llm = DeepSeekLLM(api_key=api_key)
        
        # 创建对话模板
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template="""你是一个有用的AI助手。请根据对话历史和用户当前的问题，给出准确、有帮助的回答。

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
            response = self.llm._call(user_input)
            return response
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

# flask_app.py
from flask import Flask, render_template, request, jsonify, session
import uuid

app = Flask(__name__)
app.secret_key = "your-secret-key-here"

# 存储用户会话
chat_sessions = {}

def get_chat_system():
    """获取或创建聊天系统实例"""
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    if session_id not in chat_sessions:
        api_key = os.getenv('DEEPSEEK_API_KEY', 'your-deepseek-api-key')
        chat_sessions[session_id] = ChatSystem(api_key)
    
    return chat_sessions[session_id]

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/single_chat', methods=['POST'])
def single_chat():
    """单轮对话API"""
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400
        
        chat_system = get_chat_system()
        response = chat_system.single_turn_chat(user_input)
        
        return jsonify({
            'response': response,
            'type': 'single'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/multi_chat', methods=['POST'])
def multi_chat():
    """多轮对话API"""
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400
        
        chat_system = get_chat_system()
        response = chat_system.multi_turn_chat(user_input)
        
        return jsonify({
            'response': response,
            'type': 'multi'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """获取对话历史"""
    try:
        chat_system = get_chat_system()
        history = chat_system.get_chat_history()
        return jsonify({'history': history})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """清空对话历史"""
    try:
        chat_system = get_chat_system()
        chat_system.clear_history()
        return jsonify({'message': '对话历史已清空'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保有API密钥
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("警告: 请设置DEEPSEEK_API_KEY环境变量")
    
    app.run(debug=True, host='0.0.0.0', port=5000)