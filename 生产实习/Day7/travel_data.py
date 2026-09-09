TRAVEL_DATA = {
    "杭州": {
        "weather": {
            "temperature": 26,
            "condition": "小雨",
            "rain_probability": 70,
        },
        "attractions": [
            {
                "name": "西湖",
                "category": "自然",
                "ticket": 0,
                "duration_hours": 3,
                "longitude": 120.145,
                "latitude": 30.245,
            },
            {
                "name": "灵隐寺",
                "category": "人文",
                "ticket": 75,
                "duration_hours": 2.5,
                "longitude": 120.102,
                "latitude": 30.240,
            },
            {
                "name": "浙江省博物馆",
                "category": "人文",
                "ticket": 0,
                "duration_hours": 2,
                "longitude": 120.130,
                "latitude": 30.253,
            },
            {
                "name": "河坊街",
                "category": "美食",
                "ticket": 0,
                "duration_hours": 2,
                "longitude": 120.170,
                "latitude": 30.238,
            },
            {
                "name": "西溪国家湿地公园",
                "category": "自然",
                "ticket": 80,
                "duration_hours": 3,
                "longitude": 120.067,
                "latitude": 30.271,
            },
            {
                "name": "杭州东站",
                "category": "交通",
                "ticket": 0,
                "duration_hours": 0,
                "longitude": 120.213,
                "latitude": 30.290,
            },
        ],
    },
    "北京": {
        "weather": {
            "temperature": 28,
            "condition": "晴",
            "rain_probability": 10,
        },
        "attractions": [
            {
                "name": "故宫博物院",
                "category": "人文",
                "ticket": 60,
                "duration_hours": 4,
                "longitude": 116.397,
                "latitude": 39.916,
            },
            {
                "name": "天坛公园",
                "category": "人文",
                "ticket": 34,
                "duration_hours": 2.5,
                "longitude": 116.417,
                "latitude": 39.883,
            },
            {
                "name": "颐和园",
                "category": "自然",
                "ticket": 30,
                "duration_hours": 4,
                "longitude": 116.275,
                "latitude": 39.999,
            },
            {
                "name": "南锣鼓巷",
                "category": "美食",
                "ticket": 0,
                "duration_hours": 2,
                "longitude": 116.403,
                "latitude": 39.937,
            },
            {
                "name": "北京南站",
                "category": "交通",
                "ticket": 0,
                "duration_hours": 0,
                "longitude": 116.379,
                "latitude": 39.865,
            },
        ],
    },
    "上海": {
        "weather": {
            "temperature": 27,
            "condition": "多云",
            "rain_probability": 30,
        },
        "attractions": [
            {
                "name": "外滩",
                "category": "城市风光",
                "ticket": 0,
                "duration_hours": 2,
                "longitude": 121.490,
                "latitude": 31.240,
            },
            {
                "name": "上海博物馆",
                "category": "人文",
                "ticket": 0,
                "duration_hours": 3,
                "longitude": 121.475,
                "latitude": 31.228,
            },
            {
                "name": "豫园",
                "category": "人文",
                "ticket": 40,
                "duration_hours": 2,
                "longitude": 121.492,
                "latitude": 31.227,
            },
            {
                "name": "南京路步行街",
                "category": "美食",
                "ticket": 0,
                "duration_hours": 2,
                "longitude": 121.481,
                "latitude": 31.235,
            },
            {
                "name": "上海虹桥站",
                "category": "交通",
                "ticket": 0,
                "duration_hours": 0,
                "longitude": 121.327,
                "latitude": 31.200,
            },
        ],
    },
}


def find_place(place_name: str):
    """根据地点名称查询地点数据。"""

    for city, city_data in TRAVEL_DATA.items():
        for place in city_data["attractions"]:
            if place["name"] == place_name:
                result = place.copy()
                result["city"] = city
                return result

    return None