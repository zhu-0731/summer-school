from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr
import os

# 初始化 DeepSeek 聊天模型

api_key_value = "sk-18d51b269b894f50bfc82dbd1db4cf23"
chat_model = ChatDeepSeek(
    model="deepseek-chat",  # 使用 DeepSeek 的聊天模型
    api_key=SecretStr(api_key_value),  # 使用 SecretStr 包装 API 密钥
)

# 初始化对话记忆
# ConversationBufferMemory 会记录所有对话历史
memory = ConversationBufferMemory()

# 创建对话链，绑定聊天模型和记忆
conversation = ConversationChain(
    llm=chat_model,
    memory=memory,
    verbose=True  # 打印对话过程，便于调试
)

# 示例对话
print("开始对话，输入 'exit' 退出。")
while True:
    user_input = input("你: ")
    if user_input.lower() == "exit":
        print("对话结束。")
        break
    # 调用对话链，生成回复
    response = conversation.run(user_input)
    print(f"AI: {response}")