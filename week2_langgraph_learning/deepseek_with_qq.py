#邮件工具测试，依赖关系：引用qq_tool工具，在qq_tool.py中定义了qq_mail_search工具
# 依赖于qq_mail_read.py中的fetch_subjects函数

# from langchain.llms import ChatOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from qq_tool import SearchArgs, qq_mail_search


load_dotenv()

api_key_value = os.getenv("DEEPSEEK_API_KEY")
if not api_key_value:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=SecretStr(api_key_value),  # 使用 SecretStr 包装 API 密钥
    )

# 定义状态模型
class MailState(BaseModel):
    query_result: str = ""


# 4. 定义状态图中的执行节点
def query_mail_node(state):
    # 创建参数对象
    args = SearchArgs(keyword="会议", max_results=2)
    # 调用工具
    try:
        args = SearchArgs(keyword="会议", max_results=2)
        result = qq_mail_search.invoke({"keyword": "会议", "max_results": 2})  # 传 dict，Pylance 不报错
    except Exception as e:
        result = f"调用工具异常：{e}"
    print("查询结果:", result)
    # 这里可把结果写入 state 或传递给后续节点
    return state

# 构造状态图
graph = StateGraph(MailState)  # 使用 MailState 作为 state_schema
graph.add_node("query_mail", RunnableLambda(query_mail_node))
graph.set_entry_point("query_mail")
graph.add_edge("query_mail",END)

# 编译并执行图
executor = graph.compile()
initial_state = MailState()  # 初始化状态
final_state = executor.invoke(initial_state)
print("最终状态:", final_state)

