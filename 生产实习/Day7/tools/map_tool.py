import os
import uuid

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from langchain_core.tools import tool

from travel_data import find_place


plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
]
plt.rcParams["axes.unicode_minus"] = False

os.makedirs("maps", exist_ok=True)


@tool
def make_trip_map(
    city: str,
    places: list[str],
    day: int = 1,
) -> str:
    """
    为某一天的旅行地点生成地图标注图片。

    Args:
        city: 目的地城市。
        places: 按游览顺序排列的地点名称列表。
        day: 行程的第几天。

    Returns:
        生成的PNG地图路径。
    """

    matched_places = []

    for name in places:
        place = find_place(name)

        if place is not None and place["city"] == city:
            matched_places.append(place)

    if not matched_places:
        return "错误：没有找到可用于地图标注的地点"

    longitudes = [
        place["longitude"]
        for place in matched_places
    ]

    latitudes = [
        place["latitude"]
        for place in matched_places
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(
        longitudes,
        latitudes,
        marker="o",
        linestyle="--",
        color="#2563eb",
        linewidth=2,
    )

    for index, place in enumerate(
        matched_places,
        start=1,
    ):
        ax.scatter(
            place["longitude"],
            place["latitude"],
            s=110,
            color="#ef4444",
            zorder=3,
        )

        ax.annotate(
            f"{index}. {place['name']}",
            (
                place["longitude"],
                place["latitude"],
            ),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=10,
        )

    ax.set_title(f"{city}第{day}天行程地图")
    ax.set_xlabel("经度")
    ax.set_ylabel("纬度")
    ax.grid(alpha=0.25)

    plt.tight_layout()

    file_id = uuid.uuid4().hex[:8]

    path = os.path.join(
        "maps",
        f"trip_map_day_{day}_{file_id}.png",
    )

    fig.savefig(path, dpi=130)
    plt.close(fig)

    return f"地图已保存：{path}"