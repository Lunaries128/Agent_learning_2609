import json
from tools import get_weather,get_clothing_advice,get_travel_advice
from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

model = ChatOpenAI(model="qwen3.7-max")
# 给模型绑定工具
model_with_tools = model.bind_tools([get_weather,get_clothing_advice,get_travel_advice])

TOOLS = {t.name:t for t in [get_weather,get_clothing_advice,get_travel_advice]}

SYSTEM_PROMPT = """
        你是一个智能出行助手，当用户询问出行相关的问题时候，你需要:\n
        1.先查询天气的情况\n
        2.根据天气数据查询穿衣建议\n
        3.根据天气状况查询出行建议\n
        4.综合所有的信息，给出完整、友好的出行建议\n
        请确保每一步都调用对应的工具来获取数据，不要凭空编造数据
        """
messages = [
    {"role":"system","content":SYSTEM_PROMPT}
]
while True:
    city = input("输出城市名称(quit 退出):").strip()
    if city == "quit":
        break
    messages.append({"role":"system","content":f"我明天要去{city}出差，请给出出行建议"})

    while True:
        response = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            print(f"AI最终的建议:{response.content}")
            break

        for tool_call in response.tool_calls:
            result = TOOLS[tool_call["name"]].invoke(tool_call["args"])
            messages.append(json.dumps(result,ensure_ascii=False))





