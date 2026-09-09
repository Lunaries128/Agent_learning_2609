import os
import time

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

from llm import llm
from tools.csv_tool import read_csv
from tools.sql_tool import sql_query
from tools.stats_tool import (
    stats_summary,
    stats_value_counts,
    stats_group_agg,
)
from tools.chart_tool import make_chart
from tools.calculator_tool import calculator


CHAT_SYSTEM_PROMPT = """
你是一名通用AI聊天助手。

规则：

- 正常回答知识、编程、学习、写作和生活问题。
- 自然地与用户聊天。
- 根据历史消息理解上下文。
- 不要主动谈论CSV或数据分析。
- 不要把普通问题强行联系到数据。
- 使用清晰、自然的中文回答。
"""


DATA_SYSTEM_PROMPT = """
你是一名同时具备普通聊天和数据分析能力的AI助手。

当前用户已经打开了数据分析功能。

规则：

- 用户询问普通问题时，可以直接回答。
- 用户询问当前CSV数据时，自主调用数据工具。
- 不要因为数据分析开关已打开，
  就把每一个问题都强行联系到CSV。
- 用户明确提到文件、列、数据、统计或图表时，
  才考虑调用数据工具。
- 根据历史消息理解“刚才的结果”等表达。

工具规则：

- 查看文件结构、列名和预览时调用read_csv。
- 统计所有数值列时调用stats_summary。
- 统计某列各值数量时调用stats_value_counts。
- 分组统计时调用stats_group_agg。
- 复杂筛选和查询时调用sql_query。
- 生成图表时调用make_chart。
- 数学运算时调用calculator。
- 不确定列名时先调用read_csv。
- 不得编造CSV中不存在的数据。
- 必须根据工具返回结果回答。
- 图表生成后解释图表表达的内容。
"""


data_agent = create_agent(
    model=llm,
    tools=[
        read_csv,
        sql_query,
        stats_summary,
        stats_value_counts,
        stats_group_agg,
        make_chart,
        calculator,
    ],
    system_prompt=DATA_SYSTEM_PROMPT,
)


# 每个会话保存两份历史
# 普通聊天历史和数据分析历史彼此独立
_chat_sessions: dict[str, list] = {}
_data_sessions: dict[str, list] = {}


def content_to_text(content) -> str:
    """兼容不同模型的返回格式。"""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, str):
                parts.append(block)

            elif isinstance(block, dict):
                text = block.get("text")

                if text:
                    parts.append(text)

        return "".join(parts)

    return str(content) if content else ""


def run_normal_chat(
    session_id: str,
    user_input: str,
) -> dict:
    """关闭数据分析开关时执行普通聊天。"""

    history = _chat_sessions.setdefault(
        session_id,
        [],
    )

    history.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    model_messages = [
        SystemMessage(
            content=CHAT_SYSTEM_PROMPT
        )
    ]

    model_messages.extend(history)

    response = llm.invoke(
        model_messages
    )

    reply = content_to_text(
        response.content
    )

    if not reply:
        reply = "模型没有返回文本内容。"

    history.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    return {
        "reply": reply,
        "images": [],
        "data_mode": False,
    }


def run_data_chat(
    session_id: str,
    user_input: str,
    csv_path: str,
) -> dict:
    """打开数据分析开关时执行数据Agent。"""

    history = _data_sessions.setdefault(
        session_id,
        [],
    )

    data_question = (
        f"当前CSV文件路径：{csv_path}\n\n"
        f"用户问题：{user_input}"
    )

    history.append(
        {
            "role": "user",
            "content": data_question,
        }
    )

    before = (
        set(os.listdir("charts"))
        if os.path.exists("charts")
        else set()
    )

    result = data_agent.invoke(
        {
            "messages": history,
        },
        config={
            "recursion_limit": 30,
        },
    )

    _data_sessions[session_id] = (
        result["messages"]
    )

    time.sleep(0.1)

    after = (
        set(os.listdir("charts"))
        if os.path.exists("charts")
        else set()
    )

    new_charts = [
        os.path.join("charts", filename)
        for filename in sorted(after - before)
    ]

    reply = content_to_text(
        result["messages"][-1].content
    )

    if not reply:
        reply = "数据分析Agent没有返回文本内容。"

    return {
        "reply": reply,
        "images": new_charts,
        "data_mode": True,
    }


def chat(
    session_id: str,
    user_input: str,
    data_mode: bool,
    csv_path: str = "",
) -> dict:
    """根据开关状态选择普通聊天或数据分析。"""

    if data_mode:
        if not csv_path:
            return {
                "reply": "请先上传CSV文件。",
                "images": [],
                "data_mode": True,
            }

        return run_data_chat(
            session_id=session_id,
            user_input=user_input,
            csv_path=csv_path,
        )

    return run_normal_chat(
        session_id=session_id,
        user_input=user_input,
    )


def clear_session(
    session_id: str,
) -> None:
    """清空同一个会话的普通与数据历史。"""

    _chat_sessions.pop(
        session_id,
        None,
    )

    _data_sessions.pop(
        session_id,
        None,
    )