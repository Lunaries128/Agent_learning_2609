import uuid

import dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import RunnableWithMessageHistory


# =========================
# 1. 加载环境变量
# =========================

dotenv.load_dotenv()


# =========================
# 2. 设置 Streamlit 页面
# =========================

st.set_page_config(
    page_title="智能旅行规划助手",
    page_icon="🧳",
    layout="wide",
)

st.title("🧳 智能旅行规划助手")

st.caption(
    "告诉我你的出发地、目的地、旅行天数、人数、预算和偏好。"
)


# =========================
# 3. 初始化模型
# =========================

chat_model = ChatOpenAI(
    model="qwen3.8-max",
    streaming=True,
    stream_usage=True,
)


# =========================
# 4. 编写旅行规划 Prompt
# =========================

SYSTEM_PROMPT = """
你是一名智能旅行规划助手。

你的任务是通过多轮对话了解用户的旅行需求，
并在信息基本完整后生成一份旅行方案。

你需要了解的信息包括：

1. 用户从哪里出发
2. 用户想去哪里
3. 什么时候出发
4. 旅行几天
5. 一共有几个人
6. 总预算是多少
7. 用户喜欢什么
8. 用户不喜欢什么
9. 是否携带儿童或老人
10. 有没有必去的地方

对话规则：

- 如果重要信息不完整，先向用户追问。
- 每次最多询问三个问题。
- 不要重复询问用户已经回答过的问题。
- 不重要的信息可以使用合理假设。
- 使用简洁、友好的中文回答。
- 记住历史对话中的旅行需求。
- 如果用户修改需求，以用户最新说法为准。
- 如果用户要求调整已有方案，只修改相关部分。
- 不要假装已经预订酒店、车票或门票。
- 当前没有实时地图和价格查询能力。
- 开放时间、票价和交通时间只能作为参考。

当信息不足时，只向用户提问，不要提前生成完整方案。

当信息基本完整时，按照以下格式生成方案：

# 旅行方案名称

## 一、旅行概览

说明：

- 出发地
- 目的地
- 旅行时间
- 旅行天数
- 同行人数
- 总预算
- 旅行风格

## 二、每日行程

### 第 1 天：当天主题

| 时间 | 行程 | 地点 | 交通建议 | 预计费用 |
|---|---|---|---|---:|
| 09:00-11:00 | 具体活动 | 具体地点 | 交通方式 | 费用 |

每天都按照这个格式安排。

规划每日行程时：

- 不要安排得过于紧凑。
- 需要考虑吃饭和休息。
- 同一天的地点尽量不要距离太远。
- 如果有老人或儿童，要适当减少行程。
- 用户要求轻松旅行时，每天最多安排三个主要景点。

## 三、预算明细

| 类别 | 说明 | 预计费用 |
|---|---|---:|
| 往返交通 | 说明 | 金额 |
| 住宿 | 说明 | 金额 |
| 餐饮 | 说明 | 金额 |
| 门票 | 说明 | 金额 |
| 市内交通 | 说明 | 金额 |
| 其他 | 说明 | 金额 |
| 合计 |  | 金额 |

预算要求：

- 总费用尽量不要超过用户预算。
- 所有价格都要说明是估算值。
- 如果预计超出预算，要明确提醒用户。
- 不要把估算价格说成实时成交价格。

## 四、出行提醒

列出：

- 需要提前预约的项目
- 需要用户再次确认的信息
- 天气和衣物建议
- 价格可能发生变化的项目

## 五、可调整内容

告诉用户可以继续提出修改要求，例如：

- 某一天轻松一点
- 替换某个景点
- 降低预算
- 增加美食安排
"""


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),

        # LangChain 会在这里自动加入历史消息
        MessagesPlaceholder(variable_name="history"),

        ("human", "{user_input}"),
    ]
)


# =========================
# 5. 创建 LangChain
# =========================

chain = prompt | chat_model


# =========================
# 6. 初始化 Streamlit 状态
# =========================

if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

if "session_titles" not in st.session_state:
    st.session_state.session_titles = {}

if "session_order" not in st.session_state:
    st.session_state.session_order = []

if "current_session_id" not in st.session_state:
    first_session_id = str(uuid.uuid4())

    st.session_state.current_session_id = first_session_id
    st.session_state.session_order.append(first_session_id)


# =========================
# 7. 获取某个会话的历史记录
# =========================

def get_session_history(
    session_id: str,
) -> InMemoryChatMessageHistory:
    """
    根据 session_id 获取对应的聊天历史。

    如果这个会话还不存在，就新建一个。
    """

    if session_id not in st.session_state.chat_histories:
        st.session_state.chat_histories[session_id] = (
            InMemoryChatMessageHistory()
        )

    return st.session_state.chat_histories[session_id]


# =========================
# 8. 给 Chain 加上自动记忆
# =========================

chat_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="user_input",
    history_messages_key="history",
)


# =========================
# 9. 侧边栏：管理多个旅行会话
# =========================

with st.sidebar:
    st.header("旅行会话")

    if st.button(
        "➕ 新建旅行计划",
        use_container_width=True,
    ):
        new_session_id = str(uuid.uuid4())

        st.session_state.current_session_id = new_session_id
        st.session_state.session_order.append(new_session_id)

        st.rerun()

    if st.button(
        "🗑️ 清空当前对话",
        use_container_width=True,
    ):
        current_id = st.session_state.current_session_id
        current_history = get_session_history(current_id)

        current_history.clear()

        st.session_state.session_titles[current_id] = "新旅行计划"

        st.rerun()

    st.divider()
    st.caption("历史旅行计划")

    # reversed 表示最新会话显示在最上方
    for session_id in reversed(st.session_state.session_order):
        title = st.session_state.session_titles.get(
            session_id,
            "新旅行计划",
        )

        is_current = (
            session_id
            == st.session_state.current_session_id
        )

        button_type = "primary" if is_current else "secondary"

        if st.button(
            title,
            key=f"session_{session_id}",
            use_container_width=True,
            type=button_type,
        ):
            st.session_state.current_session_id = session_id
            st.rerun()


# =========================
# 10. 显示当前会话的历史消息
# =========================

current_session_id = st.session_state.current_session_id

history = get_session_history(current_session_id)

for message in history.messages:
    if message.type == "human":
        with st.chat_message(
            "user",
            avatar="🧑",
        ):
            st.markdown(message.content)

    elif message.type == "ai":
        with st.chat_message(
            "assistant",
            avatar="🧳",
        ):
            st.markdown(message.content)


# =========================
# 11. 接收用户输入
# =========================

user_input = st.chat_input(
    "例如：我想从广州去杭州玩三天，两个人，预算5000元……"
)


# =========================
# 12. 调用模型并流式输出
# =========================

if user_input:
    # 如果是当前会话的第一条消息，
    # 就把它作为侧边栏标题。
    if not history.messages:
        if len(user_input) > 18:
            session_title = user_input[:18] + "..."
        else:
            session_title = user_input

        st.session_state.session_titles[
            current_session_id
        ] = session_title

    # 显示用户消息
    with st.chat_message(
        "user",
        avatar="🧑",
    ):
        st.markdown(user_input)

    # 显示模型回答
    with st.chat_message(
        "assistant",
        avatar="🧳",
    ):

        def response_generator():
            """
            从 LangChain 获取流式响应，
            并把每一小段文本交给 Streamlit。
            """

            response_stream = chat_with_history.stream(
                {
                    "user_input": user_input,
                },
                config={
                    "configurable": {
                        "session_id": current_session_id,
                    }
                },
            )

            for chunk in response_stream:
                if chunk.content:
                    yield chunk.content

        st.write_stream(response_generator())