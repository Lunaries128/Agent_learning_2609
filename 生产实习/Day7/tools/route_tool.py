import json
import math

from langchain_core.tools import tool

from travel_data import find_place


def calculate_distance(
    longitude1: float,
    latitude1: float,
    longitude2: float,
    latitude2: float,
) -> float:
    """使用经纬度粗略计算两个地点之间的直线距离。"""

    earth_radius = 6371

    lat1 = math.radians(latitude1)
    lat2 = math.radians(latitude2)

    delta_lat = math.radians(latitude2 - latitude1)
    delta_lon = math.radians(longitude2 - longitude1)

    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    angle = 2 * math.atan2(
        math.sqrt(value),
        math.sqrt(1 - value),
    )

    return earth_radius * angle


@tool
def estimate_route(
    start: str,
    destination: str,
    transport_mode: str = "公交",
) -> str:
    """
    估算两个景点之间的距离、交通时间和费用。

    Args:
        start: 出发地点名称。
        destination: 目的地点名称。
        transport_mode: 交通方式，只能是步行、公交或打车。

    Returns:
        估算距离、交通时间和费用。
    """

    start_place = find_place(start)
    destination_place = find_place(destination)

    if start_place is None:
        return json.dumps(
            {
                "success": False,
                "message": f"没有找到出发地点：{start}",
            },
            ensure_ascii=False,
        )

    if destination_place is None:
        return json.dumps(
            {
                "success": False,
                "message": f"没有找到目的地点：{destination}",
            },
            ensure_ascii=False,
        )

    if transport_mode not in ["步行", "公交", "打车"]:
        return json.dumps(
            {
                "success": False,
                "message": "交通方式只能是步行、公交或打车。",
            },
            ensure_ascii=False,
        )

    direct_distance = calculate_distance(
        start_place["longitude"],
        start_place["latitude"],
        destination_place["longitude"],
        destination_place["latitude"],
    )

    # 用1.3修正直线距离与实际道路距离的差异
    road_distance = round(direct_distance * 1.3, 2)

    if transport_mode == "步行":
        speed = 4.5
        cost = 0
    elif transport_mode == "公交":
        speed = 20
        cost = 4
    else:
        speed = 30
        cost = max(13, 13 + max(road_distance - 3, 0) * 2.5)

    duration_minutes = round(road_distance / speed * 60)

    return json.dumps(
        {
            "success": True,
            "start": start,
            "destination": destination,
            "transport_mode": transport_mode,
            "distance_km": road_distance,
            "duration_minutes": duration_minutes,
            "estimated_cost": round(cost, 2),
            "notice": "路线结果为基于坐标计算的模拟估算。",
        },
        ensure_ascii=False,
    )