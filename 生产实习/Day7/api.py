# ============ 导入部分 ============

# FastAPI：现代 Python 后端框架，用"装饰器"把普通函数变成 HTTP 接口
from fastapi import FastAPI
# CORSMiddleware：跨域中间件。浏览器默认禁止"网页 A 去请求服务 B"，
# 我们的前端(:8501)要请求后端(:8000)，属于跨域，必须放行
from fastapi.middleware.cors import CORSMiddleware
# StaticFiles：把一个文件夹变成"可网址访问的静态资源目录"
from fastapi.staticfiles import StaticFiles
# BaseModel：pydantic 的基类，用来定义"请求/响应的 JSON 长什么样"
# 它会自动做两件事：校验数据格式 + 自动生成接口文档
from pydantic import BaseModel

# 导入我们自己的 Agent 模块
import agent

# 创建 FastAPI 应用实例（就像 Streamlit 的 st.set_page_config 之于前端）
app = FastAPI(title="数据分析 Agent API")

# ---- 配置跨域放行 ----
# add_middleware：给应用"穿上一层盔甲"，每个请求先经过中间件
# 三个 * 的意思：允许任何来源、任何方法、任何头（教学图省事；
# 生产环境应把 allow_origins 写成具体的前端地址）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ---- 把 charts 文件夹挂载成静态资源 ----
# 挂载后：charts/xxx.png 这个本地文件
# 可以通过 http://localhost:8000/charts/xxx.png 这个网址直接访问
# 前端就是靠这个网址把图片显示出来的
app.mount("/charts", StaticFiles(directory="charts"), name="charts")


# ============ 定义请求/响应的数据格式 ============

# class ... (BaseModel) ：继承 pydantic 的 BaseModel
# 类里的每个"变量名: 类型"声明就是一个 JSON 字段

class ChatRequest(BaseModel):
    """前端 POST 过来的 JSON 必须长这样"""
    session_id: str      # 会话 ID：字符串类型，用来区分不同对话
    message: str         # 用户输入的问题


class ChatResponse(BaseModel):
    """后端返回给前端的 JSON 长这样"""
    reply: str                   # Agent 的文字回答
    images: list[str] = []       # 本轮生成的图表网址列表，默认空列表


# ============ 接口 1：健康检查 ============

# @app.get("/health") ：装饰器把下面的函数注册成"GET /health"接口
# 前端启动时先 ping 一下这个地址，通了说明后端活着
@app.get("/health")
def health():
    # 函数返回的字典会被 FastAPI 自动转成 JSON：{"status": "ok"}
    return {"status": "ok"}


# ============ 接口 2：核心聊天接口 ============

# @app.post(...) ：POST 请求（带数据体的请求），response_model 声明返回格式
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # 参数 req: ChatRequest 表示：FastAPI 会自动把请求体 JSON 解析成
    # ChatRequest 对象——格式不对（比如缺 message）会自动拒绝并返回 422 错误
    # 这就是用 BaseModel 的好处：格式校验全自动

    # 调用 agent.py 里的 chat 函数干真正的活
    result = agent.chat(req.session_id, req.message)

    # 路径转网址：本地路径 "charts/xxx.png" -> 网址 "/charts/xxx.png"
    # replace("charts", "/charts", 1) 的 1 表示只替换第一次出现
    image_urls = [img.replace("charts", "/charts", 1) for img in result["images"]]

    # 返回 ChatResponse 对象，FastAPI 自动转成 JSON 发给前端
    return ChatResponse(reply=result["reply"], images=image_urls)
