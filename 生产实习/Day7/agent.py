import os
import time

from langchain.agents import create_agent

from llm import llm
from tools.budget_tool import calculate_trip_budget
from tools.destination_tool import search_attractions
from tools.map_tool import make_trip_map
from tools.route_tool import estimate_route
from tools.weather_tool import get_weather


SYSTEM_PROMPT = """
你是一名智能旅行规划 Agent。

你的目标是根据用户的自然语言需求，生成可执行的旅行方案。

你需要了解：

1. 出发地
2. 目的地
3. 出发日期
4. 旅行天数
5. 同行人数
6. 总预算
7. 旅行偏好
8. 是否有老人或儿童
9. 必去地点和需要避开的内容

工作规则：

- 如果缺少目的地、天数、人数或预算，先向用户追问。
- 每次最多追问三个问题。
- 不要重复询问历史消息中已有的信息。
- 用户修改需求时，以最新要求为准。
- 用户只要求修改某一天时，尽量保留其他日期。
- 不得声称已经完成酒店、车票或门票预订。

工具规则：

- 生成正式方案前必须调用 get_weather。
- 生成正式方案前必须调用 search_attractions。
- 需要判断地点距离时调用 estimate_route。
- 必须调用 calculate_trip_budget 计算最终预算。
- 完成每日行程后调用 make_trip_map 生成地图。
- 地图中的地点顺序必须与当日游览顺序一致。
- 工具调用失败时明确告诉用户，不得编造结果。
- 预算合计必须使用预算工具返回的结果。
- 当前工具使用模拟数据，最终回答中必须明确说明。

行程规则：

- 每天安排2到3个主要景点。
- 必须安排午餐、晚餐、休息和交通时间。
- 同一天的景点尽量位于相近区域。
- 用户要求轻松旅行时，每天最多安排2个主要景点。
- 有老人或儿童时降低步行强度。
- 下雨时优先安排室内景点。
- 必须保留用户明确要求的必去地点。

输出格式：

# 旅行方案名称

## 旅行概览

说明出发地、目的地、日期、天数、人数、预算和偏好。

## 天气与出行建议

说明工具查询到的天气和注意事项。

## 每日行程

每天使用表格：

| 时间 | 行程 | 地点 | 交通建议 | 预计费用 |
|---|---|---|---|---:|

## 预算明细

| 类别 | 预计费用 |
|---|---:|

说明总费用、人均费用、剩余预算或超预算金额。

## 地图

说明已经生成哪些天的地图。

## 注意事项

明确天气、景点、路线和价格是模拟数据，
实际出发前需要确认实时信息。
"""


agent = create_agent(
    model=llm,
    tools=[
        get_weather,
        search_attractions,
        estimate_route,
        calculate_trip_budget,
        make_trip_map,
    ],
    system_prompt=SYSTEM_PROMPT,
)


_sessions: dict = {}


def chat(
    session_id: str,
    user_input: str,
) -> dict:
    """
    处理一轮旅行规划对话。

    返回：
    {
        "reply": "Agent回答",
        "images": ["本轮生成的地图路径"]
    }
    """

    history = _sessions.setdefault(
        session_id,
        [],
    )

    history.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    before = (
        set(os.listdir("maps"))
        if os.path.exists("maps")
        else set()
    )

    result = agent.invoke(
        {
            "messages": history,
        }
    )

    # 保存完整消息，包括工具调用消息
    _sessions[session_id] = result["messages"]

    time.sleep(0.1)

    after = (
        set(os.listdir("maps"))
        if os.path.exists("maps")
        else set()
    )

    new_maps = [
        os.path.join("maps", filename)
        for filename in sorted(after - before)
    ]

    reply = (
        result["messages"][-1].content
        or "模型没有返回文字内容。"
    )

    return {
        "reply": reply,
        "images": new_maps,
    }