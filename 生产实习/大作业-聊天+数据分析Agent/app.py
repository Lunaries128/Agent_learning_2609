import json
from pathlib import Path
import uuid

import plotly.io as pio
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
    """创建新会话。"""

    session_id = str(
        uuid.uuid4()
    )

    st.session_state.sessions[
        session_id
    ] = {
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


def render_plotly_chart(
    chart_url: str,
) -> None:
    """从后端读取并显示 Plotly 图表。"""

    try:
        response = requests.get(
            f"{API_URL}{chart_url}",
            timeout=15,
        )

        response.raise_for_status()

        figure = pio.from_json(
            response.text
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": (
                        "data_analysis_chart"
                    ),
                    "scale": 2,
                },
            },
        )

    except Exception as error:
        st.warning(
            f"图表加载失败：{error}"
        )


def render_chart_info(
    chart_info: dict | None,
) -> None:
    """展示图表计算依据。"""

    if not chart_info:
        return

    chart_state = chart_info.get(
        "chart_state",
        {},
    )

    metadata = chart_info.get(
        "metadata",
        {},
    )

    preview = chart_info.get(
        "preview",
        [],
    )

    with st.expander(
        "查看图表计算依据"
    ):
        column1, column2 = st.columns(2)

        with column1:
            st.write(
                "**图表类型：**",
                chart_state.get(
                    "chart_type",
                    "未知",
                ),
            )

            st.write(
                "**分析维度：**",
                chart_state.get(
                    "dimension",
                    "未知",
                ),
            )

            st.write(
                "**分析指标：**",
                chart_state.get(
                    "metric"
                ) or "记录数量",
            )

        with column2:
            st.write(
                "**聚合方式：**",
                chart_state.get(
                    "aggregation",
                    "未知",
                ),
            )

            st.write(
                "**排序方式：**",
                chart_state.get(
                    "sort",
                    "未知",
                ),
            )

            st.write(
                "**显示数量：**",
                chart_state.get(
                    "top_n",
                    "未知",
                ),
            )

        st.write(
            "**原始数据行数：**",
            metadata.get(
                "source_rows",
                "未知",
            ),
        )

        st.write(
            "**删除无效行数：**",
            metadata.get(
                "removed_rows",
                "未知",
            ),
        )

        if preview:
            st.write(
                "**实际绘图数据预览：**"
            )

            st.dataframe(
                preview,
                use_container_width=True,
            )


def read_stream_response(
    session_id: str,
    user_input: str,
    session: dict,
    result: dict,
):
    """
    读取 FastAPI 返回的 NDJSON。

    每收到一个 delta，
    就立即交给 st.write_stream 显示。
    """

    with requests.post(
        f"{API_URL}/chat/stream",
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
        stream=True,
        timeout=180,
    ) as response:
        response.raise_for_status()

        for raw_line in response.iter_lines():
            if not raw_line:
                continue

            line = raw_line.decode(
                "utf-8"
            )

            event = json.loads(
                line
            )

            event_type = event.get(
                "type"
            )

            if event_type == "delta":
                content = event.get(
                    "content",
                    "",
                )

                if content:
                    yield content

            elif event_type == "final":
                result["charts"] = event.get(
                    "charts",
                    [],
                )

                result["chart_info"] = (
                    event.get(
                        "chart_info"
                    )
                )

                result["data_mode"] = (
                    event.get(
                        "data_mode",
                        session[
                            "data_mode"
                        ],
                    )
                )

            elif event_type == "error":
                raise RuntimeError(
                    event.get(
                        "message",
                        "Agent 运行失败",
                    )
                )


# ==================================================
# 初始化 Streamlit 状态
# ==================================================

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

session = st.session_state.sessions[
    session_id
]


# ==================================================
# 侧边栏
# ==================================================

with st.sidebar:
    st.header("功能栏")

    data_mode = st.toggle(
        "启用数据分析",
        value=session["data_mode"],
        help=(
            "打开后可以上传 CSV 并调用数据分析工具；"
            "关闭后为普通聊天。"
        ),
        key=f"data_toggle_{session_id}",
    )

    session["data_mode"] = data_mode

    if data_mode:
        st.success(
            "数据分析功能已开启"
        )

        uploaded_file = st.file_uploader(
            "上传 CSV 文件",
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

            if (
                session["csv_path"]
                != str(saved_path)
                or not saved_path.exists()
            ):
                saved_path.write_bytes(
                    uploaded_file.getbuffer()
                )

            session["csv_path"] = str(
                saved_path
            )

            session["csv_name"] = safe_name

        if session["csv_path"]:
            st.success(
                "上传成功，当前文件："
                f"{session['csv_name']}"
            )

        else:
            st.warning(
                "请先上传 CSV 文件"
            )

    else:
        st.info(
            "当前为普通聊天"
        )

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
                    "session_id": (
                        session_id
                    ),
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
            st.session_state.sessions[
                history_id
            ]
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
            (
                st.session_state
                .current_session_id
            ) = history_id

            st.rerun()


# ==================================================
# 主页面
# ==================================================

st.title("📋 智能聊天助手")


if session["data_mode"]:
    st.caption(
        "当前可以针对侧边栏上传的 "
        "CSV 文件进行智能分析"
    )

else:
    st.caption(
        "当前为普通聊天，"
        "不会读取或分析 CSV 文件"
    )


# 检查后端
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


# 显示历史消息
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

        for chart_url in message.get(
            "charts",
            [],
        ):
            render_plotly_chart(
                chart_url
            )

        render_chart_info(
            message.get(
                "chart_info"
            )
        )

        # 兼容旧版 PNG
        for image_url in message.get(
            "images",
            [],
        ):
            st.image(
                f"{API_URL}{image_url}"
            )


# 输入框状态
if session["data_mode"]:
    input_placeholder = (
        "输入数据分析问题……"
    )

    input_disabled = not bool(
        session["csv_path"]
    )

else:
    input_placeholder = (
        "输入聊天内容……"
    )

    input_disabled = False


user_input = st.chat_input(
    input_placeholder,
    disabled=input_disabled,
)


# ==================================================
# 发送消息并流式显示
# ==================================================

if user_input:
    if not session["messages"]:
        title = user_input.strip()

        if len(title) > 16:
            title = (
                title[:16] + "..."
            )

        session["title"] = title

    session["messages"].append({
        "role": "user",
        "content": user_input,
        "charts": [],
        "chart_info": None,
    })

    with st.chat_message(
        "user",
        avatar=":material/person:",
    ):
        st.markdown(user_input)

    result = {
        "charts": [],
        "chart_info": None,
        "data_mode": (
            session["data_mode"]
        ),
    }

    reply = ""

    with st.chat_message(
        "assistant",
        avatar=":material/smart_toy:",
    ):
        try:
            reply = st.write_stream(
                read_stream_response(
                    session_id=(
                        session_id
                    ),
                    user_input=(
                        user_input
                    ),
                    session=session,
                    result=result,
                )
            )

            if not reply:
                reply = (
                    "模型没有返回文本内容。"
                )

            for chart_url in result.get(
                "charts",
                [],
            ):
                render_plotly_chart(
                    chart_url
                )

            render_chart_info(
                result.get(
                    "chart_info"
                )
            )

        except requests.exceptions.RequestException as error:
            reply = (
                f"请求后端失败：{error}"
            )

            st.error(reply)

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as error:
            reply = (
                f"流式数据解析失败：{error}"
            )

            st.error(reply)

        except RuntimeError as error:
            reply = (
                f"Agent 运行失败：{error}"
            )

            st.error(reply)

        except Exception as error:
            reply = (
                f"程序运行错误：{error}"
            )

            st.error(reply)

    session["messages"].append({
        "role": "assistant",
        "content": reply,
        "charts": result.get(
            "charts",
            [],
        ),
        "chart_info": result.get(
            "chart_info"
        ),
    })