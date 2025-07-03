#ollama测试文件，未被引用，可以删除

from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOllama
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# 设置API基础URL
api_base_url = "https://b1fa-2001-250-401-6601-7582-6476-c45a-4df0.ngrok-free.app"

# 创建聊天模型实例
chat = ChatOllama(
    base_url=api_base_url,
    model="deepseek-r1:14b",
    temperature=0.7,
)

def get_chat_response(user_input):
    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个有帮助的AI助手。"),
        HumanMessage(content=user_input)
    ]
    
    # 获取回复
    response = chat(messages)
    return response.content

# 主程序
# if __name__ == "__main__":
#     # 获取用户输入
#     user_input = input("请输入您的问题：")
    
#     # 获取并打印回复
#     try:
#         response = get_chat_response(user_input)
#         print("\nAI回复：", response)
#     except Exception as e:
#         print(f"发生错误：{str(e)}")