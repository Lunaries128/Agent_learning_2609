# ============ 导入部分 ============

# create_agent：LangChain 的"Agent 生成器"，一行创建会自主调用工具的智能体
# 它内部托管了完整循环：模型说要用工具 -> 执行 -> 结果回填 -> 模型继续 -> …直到回答
from langchain.agents import create_agent

# 从我们自己的文件里导入配置好的模型和五个工具
from llm import llm
from tools.csv_tool import read_csv
from tools.sql_tool import sql_query
from tools.stats_tool import stats_summary, stats_value_counts, stats_group_agg
from tools.chart_tool import make_chart
from tools.calculator_tool import calculator

# ============ 创建 Agent：一行，前面 Day1-8 的全部成果在这里合体 ============

agent = create_agent(
    model=llm,                                    # 大脑：用哪个模型思考
    tools=[read_csv, sql_query, stats_summary,    # 工具箱：7 个工具全部挂上
           stats_value_counts, stats_group_agg,
           make_chart, calculator],
)

# ============ 会话记忆：最朴素的实现 ============

# _sessions 是一个字典：键是会话 ID，值是该会话的完整消息历史
# { "abc123": [用户消息1, AI回复1, ...], "xyz789": [...] }
# 下划线开头 = Python 惯例，表示"本文件内部使用"
# 局限（要告诉学生）：存在内存里，后端重启就全丢；生产环境应换 Redis
_sessions: dict = {}


def chat(session_id: str, user_input: str) -> dict:
    """
    处理一轮对话。
    返回 {'reply': 回答文本, 'images': 本轮新生成的图表路径列表}
    """
    # ---------- 第 1 步：取出（或初始化）该会话的历史 ----------
    # setdefault 的意思："有就拿出来，没有就先存个空列表再拿出来"
    # 相当于：if session_id 不在字典里: 字典[session_id] = [] 然后取值
    history = _sessions.setdefault(session_id, [])

    # 把用户这轮说的话追加到历史末尾
    history.append({"role": "user", "content": user_input})

    # ---------- 第 2 步：记录"画图前"charts 目录里有哪些文件 ----------
    # 为什么？因为工具只返回"图存到哪了"这句话，
    # 我们要靠"对比目录前后差异"找出本轮新画的图，才能给前端展示
    import os, time                       # 就近导入：只有这里用到
    # os.listdir(目录) 列出目录里所有文件名；目录不存在就当空集合
    before = set(os.listdir("charts")) if os.path.exists("charts") else set()

    # ---------- 第 3 步：运行 Agent（核心一步！）----------
    # agent.invoke 会自动完成整个循环：
    #   模型思考 -> 决定调用 read_csv -> 执行 -> 结果回填 -> 决定调用 make_chart
    #   -> 执行 -> ... -> 最终生成文字回答
    # 我们不需要写任何循环代码，全由框架托管
    result = agent.invoke({"messages": history})

    # ---------- 第 4 步：把完整过程存回历史 = 有了记忆 ----------
    # 注意存的是 result["messages"]——包含中间所有工具调用消息，
    # 所以下一轮用户说"再画一张柱状图"，模型知道上一轮发生了什么
    _sessions[session_id] = result["messages"]

    # ---------- 第 5 步：对比目录，找出本轮新生成的图 ----------
    time.sleep(0.1)   # 等 0.1 秒，确保文件已经写完（防竞态小技巧）
    after = set(os.listdir("charts")) if os.path.exists("charts") else set()
    # 集合减法 after - before = 新出现的文件；再拼回完整路径
    new_charts = [os.path.join("charts", f) for f in (after - before)]

    # ---------- 第 6 步：整理返回 ----------
    # result["messages"][-1] ：最后一条消息 = 模型的最终回答
    # or "（模型没有返回文本）" ：如果 content 是空就用兜底文案
    reply = result["messages"][-1].content or "（模型没有返回文本）"
    return {"reply": reply, "images": new_charts}
