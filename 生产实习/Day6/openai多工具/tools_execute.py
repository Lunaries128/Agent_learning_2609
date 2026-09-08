import json

from tools import get_weather, get_clothing_advice, get_travel_advice


def execute_tool_call(tool_name:str,tool_args:dict) -> str:
    """
    根据LLM返回的函数名称以及参数，在本地执行对应的函数

    Args
        tool_name: 函数的名称
        tool_args: 函数的参数

    Returns
        执行本地函数返回的数据
    """

    if tool_name == "get_weather":
        return get_weather(**tool_args)
    elif tool_name == "get_clothing_advice":
        return get_clothing_advice(**tool_args)
    elif tool_name == "get_travel_advice":
        return get_travel_advice(**tool_args)
    else:
        return "未知的工具调用"

