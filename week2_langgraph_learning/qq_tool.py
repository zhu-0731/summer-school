import os

from langchain_core.tools import tool            # ← 正确导入
from pydantic import BaseModel, Field
from typing import List, Union
from qq_mail_read import fetch_subjects  # 假设你读取 QQ 邮箱


# 定义多输入参数模型
class SearchArgs(BaseModel):
    keyword: str
    max_results: int = 5


@tool("qq_mail_search", args_schema=SearchArgs, return_direct=True)
def qq_mail_search(keyword: str, max_results: int = 5) -> str:
    """LangChain Tool 包装：供 Agent 调用"""
    subjects = fetch_subjects(
        host="imap.qq.com",
        user=os.getenv("QQ_EMAIL_USER"),
        auth_code=os.getenv("QQ_IMAP_AUTH"),
        keyword=keyword,
        limit=max_results
    )
    if not subjects:
        return "未找到匹配邮件"
    return "\n".join(subjects)