import json

from langchain_core.tools import tool


@tool
def calculate_trip_budget(
    people: int,
    days: int,
    user_budget: float,
    intercity_transport_total: float,
    hotel_per_night: float,
    food_per_person_per_day: float,
    ticket_per_person: float,
    local_transport_per_day: float,
    other_cost: float = 0,
) -> str:
    """
    计算旅行预算、总费用、人均费用和预算差额。

    Args:
        people: 旅行总人数。
        days: 旅行天数。
        user_budget: 用户总预算。
        intercity_transport_total: 所有人的往返城际交通总费用。
        hotel_per_night: 每晚所有房间的住宿总费用。
        food_per_person_per_day: 每人每天餐饮费用。
        ticket_per_person: 每人的全部景点门票费用。
        local_transport_per_day: 所有人每天的市内交通费用。
        other_cost: 其他费用。

    Returns:
        分类预算、总费用、人均费用和预算差额。
    """

    if people <= 0:
        return json.dumps(
            {
                "success": False,
                "message": "旅行人数必须大于0。",
            },
            ensure_ascii=False,
        )

    if days <= 0:
        return json.dumps(
            {
                "success": False,
                "message": "旅行天数必须大于0。",
            },
            ensure_ascii=False,
        )

    values = [
        user_budget,
        intercity_transport_total,
        hotel_per_night,
        food_per_person_per_day,
        ticket_per_person,
        local_transport_per_day,
        other_cost,
    ]

    if any(value < 0 for value in values):
        return json.dumps(
            {
                "success": False,
                "message": "预算金额不能是负数。",
            },
            ensure_ascii=False,
        )

    hotel_nights = max(days - 1, 0)

    hotel_total = hotel_per_night * hotel_nights
    food_total = food_per_person_per_day * people * days
    ticket_total = ticket_per_person * people
    local_transport_total = local_transport_per_day * days

    total = (
        intercity_transport_total
        + hotel_total
        + food_total
        + ticket_total
        + local_transport_total
        + other_cost
    )

    difference = user_budget - total

    return json.dumps(
        {
            "success": True,
            "people": people,
            "days": days,
            "hotel_nights": hotel_nights,
            "details": {
                "往返交通": round(
                    intercity_transport_total,
                    2,
                ),
                "住宿": round(hotel_total, 2),
                "餐饮": round(food_total, 2),
                "门票": round(ticket_total, 2),
                "市内交通": round(
                    local_transport_total,
                    2,
                ),
                "其他": round(other_cost, 2),
            },
            "total": round(total, 2),
            "per_person": round(total / people, 2),
            "user_budget": round(user_budget, 2),
            "budget_difference": round(difference, 2),
            "within_budget": difference >= 0,
            "notice": "预算为课程演示使用的估算结果。",
        },
        ensure_ascii=False,
    )