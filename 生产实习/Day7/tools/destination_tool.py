import json

from langchain_core.tools import tool

from travel_data import TRAVEL_DATA


@tool
def search_attractions(
    city: str,
    preference: str = "综合",
) -> str:
    """
    根据目的地和用户偏好查询推荐景点。

    Args:
        city: 目的地城市，例如杭州、北京、上海。
        preference: 用户偏好，例如自然、人文、美食或综合。

    Returns:
        符合偏好的景点、门票和建议游玩时长。
    """

    city_data = TRAVEL_DATA.get(city)

    if city_data is None:
        return json.dumps(
            {
                "success": False,
                "city": city,
                "attractions": [],
                "message": "模拟数据中没有该城市的景点。",
            },
            ensure_ascii=False,
        )

    all_places = city_data["attractions"]

    # 交通枢纽不作为推荐景点
    attractions = [
        place
        for place in all_places
        if place["category"] != "交通"
    ]

    if preference != "综合":
        matched = [
            place
            for place in attractions
            if place["category"] in preference
            or preference in place["category"]
        ]

        if matched:
            attractions = matched

    result = []

    for place in attractions:
        result.append(
            {
                "name": place["name"],
                "category": place["category"],
                "ticket": place["ticket"],
                "duration_hours": place["duration_hours"],
            }
        )

    return json.dumps(
        {
            "success": True,
            "city": city,
            "preference": preference,
            "attractions": result,
            "notice": "景点和票价为课程演示使用的模拟数据。",
        },
        ensure_ascii=False,
    )