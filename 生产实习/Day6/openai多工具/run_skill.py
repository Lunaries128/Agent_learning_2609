import json
from openai import OpenAI
import dotenv
from tool_schema import tool_schema
from tools_execute import execute_tool_call

dotenv.load_dotenv()

client = OpenAI()

# Skill 编排 user_input 是用户的问题
def skill_run(user_input:str):
    # 目前messages里面放了一个System消息(System是目前定义LLM的角色，只要是当前会话 LLM都会遵循当前System来工作)
    messages = [
        {"role":"system","content":"""
        你是一个智能出行助手，当用户询问出行相关的问题时候，你需要:\n
        1.先查询天气的情况\n
        2.根据天气数据查询穿衣建议\n
        3.根据天气状况查询出行建议\n
        4.综合所有的信息，给出完整、友好的出行建议\n
        请确保每一步都调用对应的工具来获取数据，不要凭空编造数据
        """},
        {
            "role":"user","content":user_input
        }
    ]
    # 循环调用工具来执行当前的任务
    while True:
        response = client.chat.completions.create(
            model="qwen3.7-max",
            messages=messages,
            tools=tool_schema,
            tool_choice="auto"
        )
        # 先把用户的问题和大模型交互
        ai_message = response.choices[0].message
        # 判断初始问题是否需要调用工具
        if not ai_message.tool_calls:
            print(f"AI的最终的答案:{ai_message.content}")
            return ai_message.content
        # 把不需要调用工具的消息也加入到消息列表中
        messages.append(ai_message)
        # 如果LLM判断需要调用工具
        for tool_call in ai_message.tool_calls:
            # 获得LLM判断需要调用工具的函数名称
            func_name = tool_call.function.name
            # 获得LLM判断需要调用工具的参数列表
            func_args = json.loads(tool_call.function.arguments)
            # 利用函数执行器(自定义函数执行器)
            tool_result = json.dumps(execute_tool_call(func_name,func_args),ensure_ascii=False)

            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content":tool_result
            })

if __name__ == "__main__":
    print("="*50+"出行助手"+"="*50)
    print("输入城市名称，AI会自动给出出行的建议")
    print("输入 quit 退出")
    while True:
        city = input("请输入城市:").strip()
        if city == "quit":
            break
        if not city:
            continue

        user_input = f"我明天要去{city}出差，请给出出行建议"
        skill_run(user_input)