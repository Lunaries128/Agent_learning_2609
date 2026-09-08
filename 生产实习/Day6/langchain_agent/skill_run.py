from langchain.agents import create_agent
from langchain_agent.tools import get_weather, get_clothing_advice, get_travel_advice
from rich import print as r
import dotenv

dotenv.load_dotenv()

agent = create_agent(
    model="openai:qwen3.7-max",
    tools=[get_weather,get_clothing_advice,get_travel_advice],
)

while True:
    city = input("City(quit 退出): ").strip()
    if city == "quit":
        break
    result = agent.invoke({"messages":[{"role":"user","content":f"我明天要去{city}出差，请给出出行建议"}]})
    r(result["messages"][-1].content)

