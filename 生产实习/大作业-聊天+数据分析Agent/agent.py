import json
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

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


BASE_DIR = Path(__file__).resolve().parent
CHART_DIR = BASE_DIR / "charts"
CHART_DIR.mkdir(exist_ok=True)


CHAT_SYSTEM_PROMPT = """
你是一名通用 AI 聊天助手。

规则：

- 正常回答知识、编程、学习、写作和生活问题。
- 自然地与用户聊天。
- 根据历史消息理解上下文。
- 不要主动谈论 CSV 或数据分析。
- 不要把普通问题强行联系到数据。
- 使用清晰、自然的中文回答。
"""


DATA_SYSTEM_PROMPT = """
你是一名严谨的数据分析 Agent。

用户打开数据分析开关后，你可以针对当前 CSV
执行数据读取、统计、SQL 查询、绘图与计算。

基本规则：

- 普通问题可以直接回答，不要强行联系 CSV。
- 用户询问文件、列、统计或图表时再调用工具。
- 不确定列名时必须先调用 read_csv。
- 不得编造不存在的列、数据或分析结果。
- 必须根据工具实际返回结果回答。
- 工具返回错误时，不得把错误结果说成成功。

绘图规则：

- 生成图表时调用 make_chart。
- 必须明确 dimension、metric 和 aggregation。
- “总额、合计、总计”通常使用 sum。
- “平均、人均、均值”通常使用 mean。
- “数量、多少个、多少条”通常使用 count。
- 类别之间比较优先使用 bar。
- 时间趋势优先使用 line。
- 两个数值字段之间的关系使用 scatter。
- 单个数值字段的分布使用 hist。
- 类别超过 8 个时不要使用 pie。
- 不确定统计口径时先向用户追问，不要自行猜测。
- 图表生成后，必须说明：
  1. 使用的维度；
  2. 使用的指标；
  3. 聚合方式；
  4. 数据清理情况；
  5. 图表中的主要结论。

连续分析规则：

- 系统会提供“上一轮分析状态”。
- 用户说“换成折线图”“只看前五名”
  “改成平均值”“继续刚才的分析”时，
  必须继承上一轮状态中没有被用户修改的参数。
- 不得在用户没有要求时自行更换指标或维度。

工具选择：

- 文件结构、列名、预览：read_csv
- 数值列总体统计：stats_summary
- 类别频次：stats_value_counts
- 简单分组统计：stats_group_agg
- 复杂筛选和查询：sql_query
- 交互图表：make_chart
- 数学运算：calculator
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


# 普通聊天和数据分析的历史相互隔离
_chat_sessions: dict[str, list] = {}
_data_sessions: dict[str, list] = {}

# 单独保存最近一次结构化分析状态
_analysis_states: dict[str, dict] = {}


def content_to_text(content) -> str:
    """兼容不同模型的消息格式。"""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, str):
                parts.append(block)

            elif isinstance(block, dict):
                block_text = block.get("text")

                if block_text:
                    parts.append(block_text)

        return "".join(parts)

    return str(content) if content else ""


def trim_normal_history(
    history: list,
    max_messages: int = 20,
) -> list:
    """普通聊天只保留最近若干条消息。"""

    return history[-max_messages:]


def trim_data_history(
    messages: list,
    max_user_turns: int = 5,
) -> list:
    """
    保留最近几个完整数据分析回合。

    不能简单 messages[-20:]，因为这样可能把
    AI 工具调用和 ToolMessage 从中间切断。
    """

    user_positions = [
        index
        for index, message in enumerate(
            messages
        )
        if isinstance(
            message,
            HumanMessage,
        )
    ]

    if len(user_positions) <= max_user_turns:
        return messages

    start_index = user_positions[
        -max_user_turns
    ]

    return messages[start_index:]


def extract_chart_state(
    messages: list,
) -> dict | None:
    """从工具消息中读取最后一次成功的绘图状态。"""

    for message in reversed(messages):
        if not isinstance(
            message,
            ToolMessage,
        ):
            continue

        content = content_to_text(
            message.content
        )

        try:
            data = json.loads(content)
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            continue

        if (
            isinstance(data, dict)
            and data.get("success")
            and data.get("chart_state")
        ):
            return {
                "chart_state": data[
                    "chart_state"
                ],
                "metadata": data.get(
                    "metadata",
                    {},
                ),
                "preview": data.get(
                    "preview",
                    [],
                ),
            }

    return None


def get_new_chart_files(
    before: set[str],
) -> list[str]:
    """获取当前请求中新生成的 Plotly JSON。"""

    after = {
        path.name
        for path in CHART_DIR.glob(
            "*.json"
        )
    }

    new_files = sorted(
        after - before
    )

    return [
        str(CHART_DIR / filename)
        for filename in new_files
    ]


def run_normal_chat(
    session_id: str,
    user_input: str,
) -> dict:
    """关闭数据分析时执行普通聊天。"""

    history = _chat_sessions.setdefault(
        session_id,
        [],
    )

    history.append({
        "role": "user",
        "content": user_input,
    })

    history = trim_normal_history(
        history
    )

    model_messages = [
        SystemMessage(
            content=CHAT_SYSTEM_PROMPT
        ),
        *history,
    ]

    response = llm.invoke(
        model_messages
    )

    reply = content_to_text(
        response.content
    )

    if not reply:
        reply = "模型没有返回文本内容。"

    history.append({
        "role": "assistant",
        "content": reply,
    })

    _chat_sessions[session_id] = (
        trim_normal_history(history)
    )

    return {
        "reply": reply,
        "charts": [],
        "chart_info": None,
        "data_mode": False,
    }


def run_data_chat(
    session_id: str,
    user_input: str,
    csv_path: str,
) -> dict:
    """打开数据分析开关时执行数据 Agent。"""

    history = _data_sessions.setdefault(
        session_id,
        [],
    )

    analysis_state = (
        _analysis_states.get(
            session_id
        )
    )

    state_text = (
        json.dumps(
            analysis_state,
            ensure_ascii=False,
        )
        if analysis_state
        else "暂无上一轮分析状态"
    )

    data_question = f"""
当前 CSV 文件路径：
{csv_path}

上一轮结构化分析状态：
{state_text}

用户本轮问题：
{user_input}

请根据本轮问题决定是否继承上一轮分析参数。
只有用户要求修改的参数才需要改变。
"""

    history.append(
        HumanMessage(
            content=data_question
        )
    )

    before = {
        path.name
        for path in CHART_DIR.glob(
            "*.json"
        )
    }

    result = data_agent.invoke(
        {
            "messages": history,
        },
        config={
            "recursion_limit": 30,
        },
    )

    result_messages = result[
        "messages"
    ]

    new_state = extract_chart_state(
        result_messages
    )

    if new_state:
        _analysis_states[
            session_id
        ] = new_state

    _data_sessions[session_id] = (
        trim_data_history(
            result_messages
        )
    )

    chart_files = get_new_chart_files(
        before
    )

    reply = content_to_text(
        result_messages[-1].content
    )

    if not reply:
        reply = (
            "数据分析 Agent "
            "没有返回文本内容。"
        )

    return {
        "reply": reply,
        "charts": chart_files,
        "chart_info": new_state,
        "data_mode": True,
    }


def chat(
    session_id: str,
    user_input: str,
    data_mode: bool,
    csv_path: str = "",
) -> dict:
    """根据开关状态选择处理链路。"""

    if data_mode:
        if not csv_path:
            return {
                "reply": "请先上传 CSV 文件。",
                "charts": [],
                "chart_info": None,
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
    """清空指定会话的所有后端记忆。"""

    _chat_sessions.pop(
        session_id,
        None,
    )

    _data_sessions.pop(
        session_id,
        None,
    )

    _analysis_states.pop(
        session_id,
        None,
    )