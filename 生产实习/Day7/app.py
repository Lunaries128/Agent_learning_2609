# ============ 导入部分 ============

import os                     # 保存上传文件用
import uuid                   # 生成全球唯一的随机 ID（做会话 ID）
import requests               # 发 HTTP 请求的库（前端找后端要数据全靠它）
import streamlit as st        # Streamlit 前端库，约定小名 st

# ---- 页面基础设置（必须是最先调用的 st 命令）----
st.set_page_config(
    page_title="数据分析 Agent",   # 浏览器标签页标题
    page_icon="📊",                # 标签页图标
    layout="wide",                 # 宽屏布局
)
st.title("📊 数据分析 Agent")             # 页面大标题
st.caption("LangChain Agent + FastAPI + Streamlit")   # 标题下的小字说明

# ---- 后端地址常量 ----
API_URL = "http://localhost:8000"

# ---- 初始化"页面记忆" ----
# 重要概念：Streamlit 每次用户操作（点按钮、发消息）都会把整个脚本
# 【从头到尾重新运行一遍】！普通变量每次都会被重置。
# st.session_state 是唯一的例外——它跨"重新运行"存活，是页面的记忆
if "session_id" not in st.session_state:
    # uuid.uuid4() 生成随机唯一 ID；str() 转字符串
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    # 聊天记录：每个元素 {"role": "user"/"assistant", "content": 文字, "images": [图]}
    st.session_state.messages = []


# ---- 侧边栏：with 语法表示"以下组件都放进侧边栏" ----
with st.sidebar:
    st.header("📁 数据文件")

    # 文件上传组件：type 限制只能传 CSV
    # 用户没传文件时返回 None，传了返回文件对象
    uploaded = st.file_uploader("上传 CSV（默认使用项目自带 demo.csv）", type="csv")

    csv_path = "demo.csv"   # 默认使用项目根目录的演示文件
    if uploaded is not None:
        os.makedirs("uploads", exist_ok=True)          # 确保目录存在
        csv_path = os.path.join("uploads", uploaded.name)  # 拼保存路径
        # "wb" = 以二进制写模式打开文件
        # uploaded.getbuffer() 取出上传文件的全部内容写进去
        with open(csv_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"已保存: {csv_path}")   # 绿色成功提示

    # 展示当前用的文件 + 给用户几个示例问题
    st.info(f"当前数据文件：`{csv_path}`\n\n试试问：\n"
            "- 这个文件有哪些列？\n"
            "- 按地区统计一下销量总和\n"
            "- 把各地区的销量画成柱状图\n"
            "- 计算 (3+5)*12 等于多少")

    # 清空对话按钮
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []                       # 清空聊天记录
        st.session_state.session_id = str(uuid.uuid4())      # 换新会话 ID（后端记忆也断了）
        st.rerun()                                           # 立刻刷新页面


# ---- 健康检查：后端没开就友好提示并停止 ----
try:
    # timeout=2：最多等 2 秒，防止页面卡死
    requests.get(f"{API_URL}/health", timeout=2)
except requests.exceptions.ConnectionError:
    # ConnectionError = 连不上后端（多半是没启动 uvicorn）
    st.error("⚠️ 后端未启动！请先运行：`uvicorn api:app --port 8000`")
    st.stop()   # 停止执行后面的所有代码（页面到此为止）


# ---- 渲染历史聊天记录 ----
# 为什么每次都全量重画？因为 Streamlit 会整页重跑，
# 不重画的话上一次的对话就"消失"了
for msg in st.session_state.messages:
    # st.chat_message("user"/"assistant") ：生成带头像的聊天气泡
    with st.chat_message(msg["role"]):
        st.write(msg["content"])                  # 显示文字
        # msg.get("images", []) ：取 images 字段，没有就用空列表（get 不报错）
        for img_url in msg.get("images", []):
            st.image(f"{API_URL}{img_url}")       # 拼上后端地址显示图片


# ---- 用户输入区 ----
# 海象运算符 := ："赋值的同时判断"——输入了内容(非空)才进 if
# st.chat_input ：页面底部的聊天输入框
if user_input := st.chat_input("输入你的问题…"):
    # 步骤 1：立刻显示用户的消息（先存进记忆，再画气泡）
    st.session_state.messages.append({"role": "user", "content": user_input,
                                      "images": []})
    with st.chat_message("user"):
        st.write(user_input)

    # 步骤 2：调用后端拿回答
    with st.chat_message("assistant"):
        # st.spinner：显示"转圈圈"加载动画，装饰器内的代码执行期间生效
        with st.spinner("Agent 思考中…"):
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "message": f"（当前数据文件: {csv_path}）{user_input}",
                },
                timeout=120,
            )

            # 先检查状态码
            if response.status_code != 200:
                st.error(f"请求失败，状态码: {response.status_code}")
                st.text(response.text)
                st.stop()

            # 再安全解析 JSON
            try:
                resp = response.json()
            except requests.exceptions.JSONDecodeError:
                st.error("后端返回的内容不是有效的 JSON")
                st.text(response.text)
                st.stop()

        # 显示回答文字
        st.write(resp["reply"])
        # 显示本轮生成的图表
        for img_url in resp.get("images", []):
            st.image(f"{API_URL}{img_url}")

    # 步骤 3：把 AI 的回答也存进聊天记录
    # （这样下次页面重跑时，上面的"渲染历史"循环才能画出来）
    st.session_state.messages.append({"role": "assistant",
                                      "content": resp["reply"],
                                      "images": resp.get("images", [])})
