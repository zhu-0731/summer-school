# deepseek_graph_runner.py
import os
from typing import Dict #type: ignore
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from qq_tool import qq_mail_search   # 你的工具


load_dotenv()

# ────────────────────────────────────────────
# 1. 定义状态模型
# ────────────────────────────────────────────
class MailState(BaseModel):
    query_result: str = ""

# ────────────────────────────────────────────
# 2. 封装为类，提供 run(keyword, max_results)
# ────────────────────────────────────────────
class QQMailSearchGraph:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")

        # 如果后续想用 LLM，可以保留；否则删掉
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=SecretStr(api_key),
        )

    # ----------- 核心：外部调用入口 -------------
    def run(self, keyword: str, max_results: int = 5) -> MailState:

        # 节点函数必须 输入 MailState → 输出 MailState
        def query_mail_node(state: MailState) -> MailState:
            try:
                result = qq_mail_search.invoke({
                    "keyword": keyword,
                    "max_results": max_results
                })
            except Exception as e:
                result = f"调用工具异常：{e}"
            print("查询结果:", result)
            # 返回新的 MailState（符合签名要求）
            return MailState(query_result=result)

        # 3. 构建图
        graph = StateGraph(MailState)        # 声明 state_schema
        graph.add_node("query_mail", RunnableLambda(query_mail_node))
        graph.set_entry_point("query_mail")
        graph.add_edge("query_mail", END)
        executor = graph.compile()

        # 4. 执行
        return executor.invoke(MailState())   # type: ignore # 返回 MailState 实例

# ────────────────────────────────────────────
# 3. 简单测试
# ────────────────────────────────────────────
if __name__ == "__main__":
    runner = QQMailSearchGraph()
    final_state = runner.run(keyword="gmail", max_results=3)
    print("最终状态:", final_state)
