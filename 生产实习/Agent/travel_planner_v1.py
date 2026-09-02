import os
import streamlit as st
import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

chat_model= ChatOpenAI(
    model="qwen3.8-max",
    stream_usage=True
)

#旅行助手的系统提示词
SYSTEM_PROMPT = """
你是一名旅行规划助手。

你的任务是通过对话了解用户的旅行需求，并生成旅行方案。

开始规划前，你需要尽量了解：
1. 从哪里出发
2. 去哪里
3. 玩几天
4. 几个人
5. 总预算
6. 喜欢什么
7. 有什么特别要求

规则：
- 如果重要信息不完整，先向用户追问。
- 每次最多追问三个问题。
- 不要重复询问用户已经回答过的信息。
- 信息基本完整后，生成旅行方案。
- 暂时不具备实时联网和地图查询能力。
- 景点开放时间和价格只能作为参考，不要假装是实时数据。

生成方案时使用以下格式：

## 旅行概览

说明目的地、天数、人数、预算和旅行风格。

## 每日行程

### 第1天：主题

| 时间 | 行程 | 交通建议 | 预计费用 |
|---|---|---|---:|
| 09:00-11:00 | 活动 | 交通方式 | 金额 |

每天都按照这个格式生成。

## 预算明细

| 类别 | 预计费用 |
|---|---:|
| 往返交通 | 金额 |
| 住宿 | 金额 |
| 餐饮 | 金额 |
| 门票 | 金额 |
| 市内交通 | 金额 |
| 其他 | 金额 |
| 合计 | 金额 |

## 注意事项

说明价格是估算值，并列出需要用户进一步确认的事项。
"""


#设置页面
st.set_page_config(
    page_title="智能旅行规划助手",
    page_icon="🧳",
)

st.title("智能旅行规划助手")

st.caption(
    "告诉我你想去哪里、玩几天、几个人以及大致预算。"
)


#初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []


#清空对话按钮
if st.sidebar.button("重新开始"):
    st.session_state.messages = []
    st.rerun()


#显示以前的聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


#接收用户输入
user_input = st.chat_input(
    "例如：我想从上海去杭州玩三天……"
)


if user_input:
    # 保存用户消息
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)

    # 发送给模型的消息
    model_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    model_messages.extend(st.session_state.messages)

    # 流式展示模型回答
    with st.chat_message("assistant"):

        def response_generator():
            for chunk in chat_model.stream(model_messages):
                if chunk.content:
                    yield chunk.content

        full_response = st.write_stream(
            response_generator()
        )

    # 保存模型回答
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
        }
    )