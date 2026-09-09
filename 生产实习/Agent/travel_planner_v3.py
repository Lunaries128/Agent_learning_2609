import uuid

import dotenv
import streamlit as st
from langchain.agents import create_agent

from travel_tools import (
    calculate_trip_budget,
    get_weather,
    search_attractions,
)


# =========================
# 1. 加载环境变量
# =========================

dotenv.load_dotenv()


# =========================
# 2. 设置 Streamlit 页面
# =========================

st.set_page_config(
    page_title="智能旅行规划 Agent",
    page_icon="🧳",
    layout="wide",
)

st.title("🧳 智能旅行规划 Agent")

st.caption(
    "V3：支持多轮对话，并能自主调用天气、景点和预算工具。"
)


# =========================
# 3. Agent 系统提示词
# =========================

SYSTEM_PROMPT = """
你是一名智能旅行规划 Agent。

你的任务是通过多轮对话了解用户需求，
自主调用工具，并生成一份旅行方案。

你需要了解以下重要信息：

1. 从哪里出发
2. 去哪里
3. 什么时候出发
4. 旅行几天
5. 一共有几个人
6. 总预算是多少
7. 用户喜欢什么
8. 有没有老人或儿童
9. 有没有必去或不想去的地点

对话规则：

- 如果重要信息不足，先追问用户。
- 每次最多询问三个问题。
- 不要重复询问用户已经回答过的信息。
- 如果用户修改需求，以最新要求为准。
- 如果用户要求修改已有行程，只调整相关部分。
- 使用简洁、友好的中文回答。

工具使用规则：

- 在生成完整行程前，必须调用 search_attractions 查询景点。
- 在生成完整行程前，必须调用 get_weather 查询天气。
- 在生成完整行程前，必须调用 calculate_trip_budget 计算预算。
- 缺少目的地时，不要调用天气和景点工具。
- 缺少人数、天数或预算时，可以先向用户追问。
- 工具返回的是模拟数据，必须向用户说明。
- 不得伪造没有出现在工具结果中的实时信息。
- 预算总计必须采用 calculate_trip_budget 的计算结果。
- 不要自己重新计算或随意修改工具返回的总预算。

生成方案时使用以下格式：

# 旅行方案

## 一、旅行概览

- 出发地
- 目的地
- 旅行日期
- 旅行天数
- 同行人数
- 用户预算
- 旅行偏好

## 二、天气情况

说明天气工具返回的结果以及出行建议。

## 三、每日行程

### 第 1 天：主题

| 时间 | 行程 | 地点 | 交通建议 | 预计费用 |
|---|---|---|---|---:|
| 09:00-11:00 | 活动 | 地点 | 交通方式 | 金额 |

要求：

- 每天最多安排三个主要景点。
- 必须安排午餐、晚餐和适当休息。
- 相邻活动之间要预留交通时间。
- 有老人或儿童时适当减少活动。
- 下雨时优先安排室内活动。

## 四、预算明细

必须根据 calculate_trip_budget 的结果填写。

| 类别 | 预计费用 |
|---|---:|
| 往返交通 | 金额 |
| 住宿 | 金额 |
| 餐饮 | 金额 |
| 门票 | 金额 |
| 市内交通 | 金额 |
| 合计 | 金额 |

同时说明：

- 用户原始预算
- 方案预计费用
- 剩余预算或超预算金额
- 预计人均费用

## 五、注意事项

- 当前天气、景点和价格都是学习用模拟数据。
- 实际出发前需要重新查询。
- 提醒用户确认开放时间、预约要求和真实票价。
"""


# =========================
# 4. 创建 Agent
# =========================

agent = create_agent(
    model="openai:qwen3.7-max",
    tools=[
        get_weather,
        search_attractions,
        calculate_trip_budget,
    ],
    system_prompt=SYSTEM_PROMPT,
)


# =========================
# 5. 初始化会话状态
# =========================

if "travel_sessions" not in st.session_state:
    st.session_state.travel_sessions = {}

if "session_titles" not in st.session_state:
    st.session_state.session_titles = {}

if "session_order" not in st.session_state:
    st.session_state.session_order = []

if "current_session_id" not in st.session_state:
    session_id = str(uuid.uuid4())

    st.session_state.current_session_id = session_id
    st.session_state.session_order.append(session_id)

    st.session_state.travel_sessions[session_id] = []


# =========================
# 6. 获取当前会话消息
# =========================

def get_messages(session_id: str) -> list:
    """
    获取某个会话的历史消息。

    每个会话使用一个消息列表保存历史。
    """

    if session_id not in st.session_state.travel_sessions:
        st.session_state.travel_sessions[session_id] = []

    return st.session_state.travel_sessions[session_id]


# =========================
# 7. 侧边栏
# =========================

with st.sidebar:
    st.header("旅行计划")

    if st.button(
        "➕ 新建旅行计划",
        use_container_width=True,
    ):
        new_session_id = str(uuid.uuid4())

        st.session_state.current_session_id = new_session_id
        st.session_state.session_order.append(new_session_id)
        st.session_state.travel_sessions[new_session_id] = []

        st.rerun()

    if st.button(
        "🗑️ 清空当前对话",
        use_container_width=True,
    ):
        current_id = st.session_state.current_session_id

        st.session_state.travel_sessions[current_id] = []
        st.session_state.session_titles[current_id] = "新旅行计划"

        st.rerun()

    st.divider()
    st.caption("历史旅行计划")

    for session_id in reversed(st.session_state.session_order):
        title = st.session_state.session_titles.get(
            session_id,
            "新旅行计划",
        )

        is_current = (
            session_id
            == st.session_state.current_session_id
        )

        if st.button(
            title,
            key=f"session_{session_id}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
        ):
            st.session_state.current_session_id = session_id
            st.rerun()


# =========================
# 8. 显示历史消息
# =========================

current_session_id = st.session_state.current_session_id
messages = get_messages(current_session_id)

for message in messages:
    role = message["role"]
    content = message["content"]

    if role == "user":
        with st.chat_message(
            "user",
            avatar="🧑",
        ):
            st.markdown(content)

    elif role == "assistant":
        with st.chat_message(
            "assistant",
            avatar="🧳",
        ):
            st.markdown(content)


# =========================
# 9. 接收用户输入
# =========================

user_input = st.chat_input(
    "例如：从上海去杭州玩三天，两个人，预算5000元……"
)


# =========================
# 10. 调用 Agent
# =========================

if user_input:
    # 如果是第一条消息，将它设置成会话标题
    if not messages:
        if len(user_input) > 18:
            title = user_input[:18] + "..."
        else:
            title = user_input

        st.session_state.session_titles[
            current_session_id
        ] = title

    # 保存用户消息
    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    # 显示用户消息
    with st.chat_message(
        "user",
        avatar="🧑",
    ):
        st.markdown(user_input)

    # 调用 Agent 并显示流式结果
    with st.chat_message(
        "assistant",
        avatar="🧳",
    ):

        answer_parts = []

        def agent_response_generator():
            """
            流式调用 Agent。

            Agent 可能先调用一个或多个工具，
            然后再生成最终回答。
            """

            response_stream = agent.stream(
                {
                    "messages": messages,
                },
                stream_mode="messages",
            )

            for message_chunk, metadata in response_stream:
                content = message_chunk.content

                # 大部分普通文本块是字符串
                if isinstance(content, str) and content:
                    answer_parts.append(content)
                    yield content

        st.write_stream(agent_response_generator())

    # 把最终文本保存进当前会话
    full_answer = "".join(answer_parts)

    if not full_answer:
        full_answer = "Agent 已完成处理，但没有返回文本内容。"

    messages.append(
        {
            "role": "assistant",
            "content": full_answer,
        }
    )