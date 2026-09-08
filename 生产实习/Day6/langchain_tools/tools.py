# 导入工具的装饰器
from langchain.tools import tool

# 1.定义工具的部分
@tool
def get_weather(city:str) -> dict:
    """
    获取指定城市的天气信息

    Args
        city: 城市的名称,例如:北京，上海

    Returns
        获取到的指定城市的天气信息
    """
    mock_weather_inofs = {
        "北京": {"city": "北京", "temperature": 32, "cindition": "晴", "rain_probability": 10, "nv_index": 8},
        "上海": {"city": "上海", "temperature": 28, "cindition": "多云", "rain_probability": 30, "nv_index": 5},
        "杭州": {"city": "杭州", "temperature": 27, "cindition": "小雨", "rain_probability": 80, "nv_index": 3},
        "西安": {"city": "西安", "temperature": 32, "cindition": "晴", "rain_probability": 5, "nv_index": 9},
        "深圳": {"city": "深圳", "temperature": 31, "cindition": "雷阵雨", "rain_probability": 90, "nv_index": 4},
    }

    return mock_weather_inofs.get(city,{"city": city,"temperature": 20, "cindition": "晴", "rain_probability": 50, "nv_index": 5})

@tool
def get_clothing_advice(temperature:float,rain_probability: float, nv_index: float) -> dict:
    """
    根据天气的数据给出穿衣的建议

    Args
        temperature: 温度
        rain_probability: 降雨概率
        nv_index: 紫外线强度

    Returns
        穿衣建议
    """
    advice = []

    if temperature >=35 :
        advice.append("穿轻薄透气的短袖短裤")
    elif temperature >=25 :
        advice.append("穿短袖T恤或者薄衬衫")
    elif temperature >=15 :
        advice.append("穿长袖或者薄外套")
    else:
        advice.append("需要穿厚外套或轻薄羽绒服")

    if rain_probability>50:
        advice.append("降雨概率比较高,记得带伞")
    elif rain_probability>20:
        advice.append("有一定的降雨的概率，建议随身带伞")

    if nv_index>=8:
        advice.append("紫外线极强，务必涂防晒+戴帽子+戴墨镜")
    elif nv_index>=5:
        advice.append("紫外线较强，建议戴帽子+戴墨镜")

    return {"advice":advice}

@tool
def get_travel_advice(weather_conditon: str, temperature:float) -> dict:
    """
    根据天气信息以及温度推荐出行方式
    Args
        weather_conditon: 天气的信息
        temperature: 温度

    Returns
        出行的建议
    """
    if weather_conditon in ["大雨","雷阵雨","暴雨"]:
        recommendation = "强烈建议乘坐地铁或者打车，避免骑行和步行"
    elif weather_conditon in ["小雨","阵雨"]:
        recommendation = "建议乘坐公交或地铁,骑行需注意路面湿滑"
    elif weather_conditon == "雪":
        recommendation = "建议打车或者自驾,路面湿滑需注意安全"
    elif temperature > 35:
        recommendation = "天气炎热，建议地铁出行，避免长时间户外步行"
    elif temperature > 20:
        recommendation = "天气舒适，推荐骑行或者步行，享受好天气"
    else:
        recommendation = "天谴较冷，建议打车或乘坐公交"

    return {"recommendation":recommendation}

