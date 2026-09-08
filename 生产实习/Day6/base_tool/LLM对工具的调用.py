import json

from rich import print as rprint
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

# LLM对工具的调用
# 1.定义工具
def get_current_weather(city:str) -> str:
    """
    模拟获取指定城市的天气信息

    Args
        city: 指定的程序名称

    Returns
        指定的城市的天气的信息
    """
    weather_db={
        "北京":"晴天，气温28°C，微风",
        "上海":"多云转阴,气温25°C，东南风3级",
        "深圳":"雷阵雨,气温32°C，湿度85%"
    }

    return weather_db.get(city,f"暂时没有找到关于{city}城市的天气信息")

# 2.LLM不能直接调用函数的，只能通过promot判断是否需要调用函数
# 也就是LLM看不到python代码的，需要通过JSON格式的数据来告诉LLM指定的函数(把定义的函数告诉给LLM)
# type : function 表明当前定义的是一个函数
# function:{} 表明当前函数是一个对象 {}内部的都是描述当前函数的
# name:get_current_weather 标识当前函数的名称(需要告诉给LLM的函数名)
# description : "" 当前函数的描述(LLM判断是否调用函数的时候会读取当前描述信息来判断)
# parameters:{} 对当前函数的参数的描述 {} 是当前函数的所有的参数
# city 就是对当前函数的city参数的描述
# type : string 说明当前的city参数的类型
# description : "" 说明当前参数的描述
# required : ["city"] 说明必须的参数有哪些
tool_schema={
    "type":"function",
    "function":{
        "name":"get_current_weather",
        "description":"获取指定城市的天气信息",
        "parameters":{
            "city":{
                "type":"string",
                "description":"指定城市的名称,例如:北京"
            }
        },
        "required":["city"]
    }
}

# 创建OpenAI的实例
client = OpenAI()
messages = [
    {"role":"system","content":"你是一个天气助手，调用工具来获取指定的城市的天气信息"},
    {"role":"user","content":"北京今天的天气怎么样?"}
]
# 3.需要把工具的描述注册给LLM
# tools 是注册给LLM的工具列表(列表类型 可以注册多个工具)
# tool_choice="auto" 调用工具是由LLM判断
response = client.chat.completions.create(
    model = "qwen3.7-max",
    messages=messages,
    tools=[tool_schema],
    tool_choice="auto"
)

ai_message = response.choices[0].message

# 如果当前AIMessage的tool_calls 如果是None
if not ai_message.tool_calls:
    print("LLM判断当前的问题不需要调用工具")
    messages.append({"role":"assistant","content":ai_message.content})
else:
    print("需要调用工具")
    messages.append(ai_message)

    tool_name = ai_message.tool_calls[0].function.name
    tool_args = ai_message.tool_calls[0].function.arguments

    print(f"LLM判断需要调用工具{tool_name},参数:{tool_args}")

    # LLM不能调用定义的函数，所以需要手段的调用
    # 把字符串的{}转换成字典
    args_dict = json.loads(tool_args)
    tool_result = get_current_weather(**args_dict)
    print(f"本地调用工具的结果:{tool_result}")

    # 把本地工具执行的结果交给LLM
    messages.append({"role":"tool","tool_call_id":ai_message.tool_calls[0].id,"content":tool_result})

    final_response = client.chat.completions.create(
        model="qwen3.7-max",
        messages=messages,
        tools=[tool_schema],
        tool_choice="auto"
    )

    final_result = final_response.choices[0].message.content
    print(f"AI助手:{final_result}")
    messages.append({"role":"assistant","content":final_result})
# 输出的 ai_message
"""
messages = [
    {"role":"system","content":"你是一个天气助手，调用工具来获取指定的城市的天气信息"},
    {"role":"user","content":"你好，你是谁?"}
]
"""
"""
ChatCompletionMessage(
    content='你好！我是一个天气助手，可以帮你查询各个城市的天气信息。请问你需要
查询哪个城市的天气呢？',
    refusal=None,
    role='assistant',
    annotations=None,
    audio=None,
    function_call=None,
    tool_calls=None,
    reasoning_content='用户问“你好，你是谁?”。\n我需要回答我的身份，即我是一个
天气助手，可以调用工具来获取指定城市的天气信息。\n不需要调用任何天气工具，直接
回答即可。\n回答内容：你好！我是一个天气助手，可以帮你查询各个城市的天气信息。
请问你需要查询哪个城市的天气呢？'
)
"""

"""
messages = [
    {"role":"system","content":"你是一个天气助手，调用工具来获取指定的城市的天气信息"},
    {"role":"user","content":"北京今天的天气怎么样?"}
]
"""
"""
ChatCompletionMessage(
    content='',
    refusal=None,
    role='assistant',
    annotations=None,
    audio=None,
    function_call=None,
    tool_calls=[
        ChatCompletionMessageFunctionToolCall(
            id='call_96aab1888c434029ad710c6b',
            function=Function(
                arguments='{"city": "北京"}',
                name='get_current_weather'
            ),
            type='function',
            index=0
        )
    ],
    reasoning_content='用户询问北京今天的天气。\n我需要调用 
`get_current_weather` 函数，并传入参数 `city` 为 "北京"。'
)

"""

# 从LLM返回的AI_Message消息来看，LLM只是判断了当前的交互是需要调用函数的(tool_calls有数据) 但是LLM不能直接去调用函数
# 从上述两个问题的返回的消息来看，tool_calls