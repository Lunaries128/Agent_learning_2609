import uuid

import requests
import streamlit as st


st.set_page_config(
    page_title="智能旅行规划 Agent",
    page_icon="🧳",
    layout="wide",
)

st.title("🧳 智能旅行规划 Agent")

st.caption(
    "LangChain Agent + FastAPI + Streamlit"
)


API_URL = "http://localhost:8000"


if "session_id" not in st.session_state:
    st.session_state.session_id = str(
        uuid.uuid4()
    )

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.header("旅行需求提示")

    st.info(
        "建议告诉 Agent：\n\n"
        "- 从哪里出发\n"
        "- 去哪个城市\n"
        "- 什么时候出发\n"
        "- 旅行几天\n"
        "- 一共几个人\n"
        "- 总预算\n"
        "- 喜欢什么\n"
        "- 是否带老人或儿童\n"
        "- 有没有必去景点"
    )

    st.caption(
        "当前天气、景点、路线和价格使用模拟数据。"
    )

    if st.button(
        "🗑️ 清空旅行计划",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.session_id = str(
            uuid.uuid4()
        )
        st.rerun()


try:
    health_response = requests.get(
        f"{API_URL}/health",
        timeout=2,
    )

    health_response.raise_for_status()

except requests.exceptions.RequestException:
    st.error(
        "后端未启动，请先运行："
        "`uvicorn api:app --reload --port 8000`"
    )
    st.stop()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        for image_url in message.get(
            "images",
            [],
        ):
            st.image(
                f"{API_URL}{image_url}"
            )


user_input = st.chat_input(
    "例如：从上海去杭州玩3天，两个人，预算5000元……"
)


if user_input:
    user_message = {
        "role": "user",
        "content": user_input,
        "images": [],
    }

    st.session_state.messages.append(
        user_message
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner(
            "Agent正在查询并规划……"
        ):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "session_id": (
                            st.session_state.session_id
                        ),
                        "message": user_input,
                    },
                    timeout=180,
                )

                response.raise_for_status()
                result = response.json()

            except requests.exceptions.RequestException as error:
                st.error(
                    f"请求后端失败：{error}"
                )
                st.stop()

            except ValueError:
                st.error(
                    "后端返回的不是有效JSON。"
                )
                st.stop()

        st.markdown(result["reply"])

        for image_url in result.get(
            "images",
            [],
        ):
            st.image(
                f"{API_URL}{image_url}",
                caption="Agent生成的行程地图",
            )

    assistant_message = {
        "role": "assistant",
        "content": result["reply"],
        "images": result.get("images", []),
    }

    st.session_state.messages.append(
        assistant_message
    )