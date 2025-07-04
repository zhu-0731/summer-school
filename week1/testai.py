from chatwith_API import ChatSystem 
from langchain.llms import ChatDeepSeek

def main():

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
