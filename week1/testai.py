from chatwith_API import ChatSystem 
from langchain.llms import ChatDeepSeek

def main():
    # # 初始化ChatSystem
    # api_key = "sk-f32eb4825d1740fbb81ee8d6bf8c3644"  # 替换为你的DeepSeek API密钥     
    # chat_system = ChatSystem(api_key)
    # # 测试单轮对话
    # user_input = "你好，今天的天气怎么样？"
    # response = chat_system.single_turn_chat(user_input)
    # print(f"单轮对话响应: {response}")
    # # 测试多轮对话
    # user_input = "请告诉我一些关于Python编程的知识。"
    # response = chat_system.multi_turn_chat(user_input) 
    # print(f"多轮对话响应: {response}")

    llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="your api key",  # 注意：这里的 API Key 应该是您自己的密钥
    )

    # 定义对话消息
    messages = [
        ("system", "你是讲故事高手，给用户讲一些有趣幽默的小故事，输出字数不超过50个字"),
        ("human", "我是初中生，给我讲一个故事"),
    ]

    # 流式输出故事内容
    for chunk in llm.stream(messages):
        print(chunk.text(), end="")

if __name__ == "__main__":
    main()    
