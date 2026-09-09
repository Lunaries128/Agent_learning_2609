import json

from langchain_core.tools import tool

from travel_data import TRAVEL_DATA


@tool
def get_weather(city: str) -> str:
    """
    查询目的地的模拟天气。

    Args:
        city: 目的地城市，例如杭州、北京、上海。

    Returns:
        温度、天气状况和降雨概率。
    """

    city_data = TRAVEL_DATA.get(city)

    if city_data is None:
        return json.dumps(
            {
                "success": False,
                "city": city,
                "message": "模拟数据中没有该城市的天气。",
            },
            ensure_ascii=False,
        )

    weather = city_data["weather"]

    return json.dumps(
        {
            "success": True,
            "city": city,
            "temperature": weather["temperature"],
            "condition": weather["condition"],
            "rain_probability": weather["rain_probability"],
            "notice": "当前为课程演示使用的模拟天气。",
        },
        ensure_ascii=False,
    )