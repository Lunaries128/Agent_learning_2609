from pathlib import Path
import uuid

import requests
import streamlit as st


st.set_page_config(
    page_title="智能聊天助手",
    page_icon="📋",
    layout="wide",
)


API_URL = "http://127.0.0.1:8000"

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def create_session() -> str:
    """创建一个新会话。"""

    session_id = str(uuid.uuid4())

    st.session_state.sessions[session_id] = {
        "title": "新对话",
        "messages": [],
        "data_mode": False,
        "csv_path": "",
        "csv_name": "",
    }

    st.session_state.session_order.append(
        session_id
    )

    st.session_state.current_session_id = (
        session_id
    )

    return session_id


if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "session_order" not in st.session_state:
    st.session_state.session_order = []

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None


if not st.session_state.session_order:
    create_session()


session_id = (
    st.session_state.current_session_id
)

session = (
    st.session_state.sessions[session_id]
)


with st.sidebar:
    st.header("功能栏")

    # 数据分析功能开关
    data_mode = st.toggle(
        "启用数据分析",
        value=session["data_mode"],
        help=(
            "打开后可以上传CSV并调用数据分析工具；"
            "关闭后为普通聊天。"
        ),
        key=f"data_toggle_{session_id}",
    )

    session["data_mode"] = data_mode

    if data_mode:
        st.success("数据分析功能已开启")

        # 文件上传移动到侧边栏
        uploaded_file = st.file_uploader(
            "上传CSV文件",
            type=["csv"],
            key=f"uploader_{session_id}",
        )

        if uploaded_file is not None:
            safe_name = Path(
                uploaded_file.name
            ).name

            saved_name = (
                f"{session_id}_{safe_name}"
            )

            saved_path = (
                    UPLOAD_DIR / saved_name
            )

            with open(saved_path, "wb") as file:
                file.write(
                    uploaded_file.getbuffer()
                )

            session["csv_path"] = str(
                saved_path
            )
            session["csv_name"] = safe_name

        if session["csv_path"]:
            st.success(
                f"上传成功，当前文件：{session['csv_name']}"
            )
        else:
            st.warning(
                "请先上传CSV文件"
            )

    else:
        st.info("当前为普通聊天")

    st.divider()

    if st.button(
        "➕ 新建对话",
        use_container_width=True,
    ):
        create_session()
        st.rerun()

    if st.button(
        "🗑️ 清空当前对话",
        use_container_width=True,
    ):
        try:
            requests.post(
                f"{API_URL}/clear",
                json={
                    "session_id": session_id,
                },
                timeout=5,
            )
        except requests.exceptions.RequestException:
            pass

        session["messages"] = []
        session["title"] = "新对话"

        st.rerun()

    st.divider()
    st.caption("历史会话")

    for history_id in reversed(
        st.session_state.session_order
    ):
        history_session = (
            st.session_state.sessions[history_id]
        )

        is_current = (
            history_id == session_id
        )

        if st.button(
            history_session["title"],
            key=f"history_{history_id}",
            use_container_width=True,
            type=(
                "primary"
                if is_current
                else "secondary"
            ),
        ):
            st.session_state.current_session_id = (
                history_id
            )
            st.rerun()


st.title("📋 智能聊天助手")


if session["data_mode"]:
    st.caption(
        "当前可以针对侧边栏上传的CSV文件进行分析"
    )
else:
    st.caption(
        "当前为普通聊天，不会读取或分析CSV文件"
    )


try:
    health_response = requests.get(
        f"{API_URL}/health",
        timeout=3,
    )

    health_response.raise_for_status()

except requests.exceptions.RequestException:
    st.error(
        "后端未启动，请先运行：\n\n"
        "`python -m uvicorn api:app "
        "--reload --port 8000`"
    )
    st.stop()


for message in session["messages"]:
    if message["role"] == "user":
        avatar = ":material/person:"
    else:
        avatar = ":material/smart_toy:"

    with st.chat_message(
        message["role"],
        avatar=avatar,
    ):
        st.markdown(
            message["content"]
        )

        for image_url in message.get(
            "images",
            [],
        ):
            st.image(
                f"{API_URL}{image_url}"
            )


if session["data_mode"]:
    input_placeholder = "输入数据分析问题……"

    input_disabled = not bool(
        session["csv_path"]
    )

else:
    input_placeholder = "输入聊天内容……"
    input_disabled = False


user_input = st.chat_input(
    input_placeholder,
    disabled=input_disabled,
)


if user_input:
    if not session["messages"]:
        title = user_input.strip()

        if len(title) > 16:
            title = title[:16] + "..."

        session["title"] = title

    session["messages"].append(
        {
            "role": "user",
            "content": user_input,
            "images": [],
        }
    )

    with st.chat_message("user",avatar=":material/person:"):
        st.markdown(user_input)

    with st.chat_message("assistant",avatar=":material/smart_toy:"):
        loading_text = (
            "Agent正在分析数据……"
            if session["data_mode"]
            else "正在回答……"
        )

        with st.spinner(loading_text):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "session_id": session_id,
                        "message": user_input,
                        "data_mode": (
                            session["data_mode"]
                        ),
                        "csv_path": (
                            session["csv_path"]
                        ),
                    },
                    timeout=180,
                )

                if response.status_code != 200:
                    try:
                        error_data = response.json()

                        error_message = (
                            error_data.get(
                                "detail",
                                response.text,
                            )
                        )

                    except ValueError:
                        error_message = response.text

                    st.error(
                        f"后端错误：{error_message}"
                    )
                    st.stop()

                result = response.json()

            except requests.exceptions.RequestException as error:
                st.error(
                    f"请求后端失败：{error}"
                )
                st.stop()

            except ValueError:
                st.error(
                    "后端没有返回有效JSON。"
                )
                st.stop()

        st.markdown(
            result["reply"]
        )

        for image_url in result.get(
            "images",
            [],
        ):
            st.image(
                f"{API_URL}{image_url}",
                caption="Agent生成的分析图表",
            )

    session["messages"].append(
        {
            "role": "assistant",
            "content": result["reply"],
            "images": result.get(
                "images",
                [],
            ),
        }
    )