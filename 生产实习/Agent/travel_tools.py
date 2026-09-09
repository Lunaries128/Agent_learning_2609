from langchain.tools import tool


@tool
def get_weather(city: str) -> dict:
    """
    查询指定城市的模拟天气。

    Args:
        city: 城市名称，例如杭州、上海、北京。

    Returns:
        城市天气、温度和降雨概率。
    """

    weather_data = {
        "北京": {
            "city": "北京",
            "temperature": 28,
            "condition": "晴",
            "rain_probability": 10,
        },
        "上海": {
            "city": "上海",
            "temperature": 27,
            "condition": "多云",
            "rain_probability": 30,
        },
        "杭州": {
            "city": "杭州",
            "temperature": 26,
            "condition": "小雨",
            "rain_probability": 70,
        },
        "西安": {
            "city": "西安",
            "temperature": 30,
            "condition": "晴",
            "rain_probability": 10,
        },
        "成都": {
            "city": "成都",
            "temperature": 25,
            "condition": "阴",
            "rain_probability": 40,
        },
    }

    return weather_data.get(
        city,
        {
            "city": city,
            "temperature": 25,
            "condition": "天气未知",
            "rain_probability": 30,
            "notice": "当前为模拟数据，请出发前查询实时天气。",
        },
    )


@tool
def search_attractions(
    city: str,
    preference: str = "综合",
) -> dict:
    """
    根据城市和用户偏好查询推荐景点。

    Args:
        city: 目的地城市，例如杭州、北京。
        preference: 用户的旅行偏好，例如人文、美食、自然。

    Returns:
        推荐景点列表及参考信息。
    """

    attraction_data = {
        "杭州": [
            {
                "name": "西湖",
                "type": "自然",
                "duration": "3小时",
                "ticket": 0,
            },
            {
                "name": "灵隐寺",
                "type": "人文",
                "duration": "2.5小时",
                "ticket": 75,
            },
            {
                "name": "浙江省博物馆",
                "type": "人文",
                "duration": "2小时",
                "ticket": 0,
            },
            {
                "name": "河坊街",
                "type": "美食",
                "duration": "2小时",
                "ticket": 0,
            },
            {
                "name": "西溪湿地",
                "type": "自然",
                "duration": "3小时",
                "ticket": 80,
            },
        ],
        "北京": [
            {
                "name": "故宫博物院",
                "type": "人文",
                "duration": "4小时",
                "ticket": 60,
            },
            {
                "name": "天坛公园",
                "type": "人文",
                "duration": "2.5小时",
                "ticket": 34,
            },
            {
                "name": "颐和园",
                "type": "自然",
                "duration": "4小时",
                "ticket": 30,
            },
            {
                "name": "南锣鼓巷",
                "type": "美食",
                "duration": "2小时",
                "ticket": 0,
            },
        ],
        "上海": [
            {
                "name": "外滩",
                "type": "城市风光",
                "duration": "2小时",
                "ticket": 0,
            },
            {
                "name": "上海博物馆",
                "type": "人文",
                "duration": "3小时",
                "ticket": 0,
            },
            {
                "name": "豫园",
                "type": "人文",
                "duration": "2小时",
                "ticket": 40,
            },
            {
                "name": "南京路步行街",
                "type": "美食",
                "duration": "2小时",
                "ticket": 0,
            },
        ],
    }

    attractions = attraction_data.get(city, [])

    if not attractions:
        return {
            "city": city,
            "preference": preference,
            "attractions": [],
            "notice": "模拟数据库中暂时没有这个城市的数据。",
        }

    # 如果用户没有明确偏好，返回全部景点
    if preference == "综合":
        selected = attractions
    else:
        # 简单地按照偏好文字进行筛选
        selected = [
            item
            for item in attractions
            if item["type"] in preference
            or preference in item["type"]
        ]

        # 如果没有匹配到，就返回全部景点
        if not selected:
            selected = attractions

    return {
        "city": city,
        "preference": preference,
        "attractions": selected,
        "notice": "当前景点与票价为学习用模拟数据。",
    }


@tool
def calculate_trip_budget(
    people: int,
    days: int,
    transport_cost: float,
    hotel_per_night: float,
    food_per_person_per_day: float,
    ticket_per_person: float,
    local_transport_per_day: float,
) -> dict:
    """
    计算旅行总预算和人均预算。

    Args:
        people: 旅行总人数。
        days: 旅行天数。
        transport_cost: 所有人的往返交通总费用。
        hotel_per_night: 每晚住宿费用。
        food_per_person_per_day: 每人每天的餐饮费用。
        ticket_per_person: 每人的全部门票费用。
        local_transport_per_day: 所有人每天的市内交通费用。

    Returns:
        各类费用、预计总费用和人均费用。
    """

    if people <= 0:
        return {
            "success": False,
            "error": "旅行人数必须大于0。",
        }

    if days <= 0:
        return {
            "success": False,
            "error": "旅行天数必须大于0。",
        }

    # 例如旅行3天，一般住宿2晚
    hotel_nights = max(days - 1, 0)

    hotel_total = hotel_per_night * hotel_nights
    food_total = food_per_person_per_day * people * days
    ticket_total = ticket_per_person * people
    local_transport_total = local_transport_per_day * days

    total = (
        transport_cost
        + hotel_total
        + food_total
        + ticket_total
        + local_transport_total
    )

    return {
        "success": True,
        "people": people,
        "days": days,
        "hotel_nights": hotel_nights,
        "details": {
            "往返交通": round(transport_cost, 2),
            "住宿": round(hotel_total, 2),
            "餐饮": round(food_total, 2),
            "门票": round(ticket_total, 2),
            "市内交通": round(local_transport_total, 2),
        },
        "total": round(total, 2),
        "per_person": round(total / people, 2),
        "notice": "预算为学习用估算结果，不代表实时价格。",
    }