import json
import re
import uuid
from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.express as px
from langchain_core.tools import tool


BASE_DIR = Path(__file__).resolve().parent.parent
CHART_DIR = BASE_DIR / "charts"
CHART_DIR.mkdir(exist_ok=True)


ChartType = Literal[
    "bar",
    "line",
    "pie",
    "scatter",
    "hist",
]

AggregationType = Literal[
    "sum",
    "mean",
    "count",
    "min",
    "max",
    "median",
]

SortType = Literal[
    "ascending",
    "descending",
    "none",
]


def read_csv_safely(
    csv_path: str,
) -> pd.DataFrame:
    """兼容常见 CSV 编码。"""

    encodings = [
        "utf-8",
        "utf-8-sig",
        "gbk",
    ]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(
                csv_path,
                encoding=encoding,
            )
        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        f"无法读取 CSV 编码：{last_error}"
    )


def convert_numeric(
    series: pd.Series,
) -> pd.Series:
    """
    将金额、百分比和带逗号的数字转换成数值。

    示例：
    ￥1,200 -> 1200
    35% -> 35
    """

    if pd.api.types.is_numeric_dtype(
        series
    ):
        return series

    cleaned = (
        series.astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace(
            r"[￥¥$元%]",
            "",
            regex=True,
        )
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    )


def normalize_category(
    series: pd.Series,
) -> pd.Series:
    """清理分类字段两侧空格。"""

    return (
        series.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


def validate_columns(
    df: pd.DataFrame,
    dimension: str,
    metric: str,
    aggregation: str,
    chart_type: str,
) -> None:
    """验证模型给出的字段是否真实存在。"""

    if dimension not in df.columns:
        raise ValueError(
            f"维度字段不存在：{dimension}。"
            f"可用字段：{list(df.columns)}"
        )

    needs_metric = (
        aggregation != "count"
        or chart_type == "scatter"
    )

    if needs_metric and not metric:
        raise ValueError(
            "当前分析必须指定指标字段 metric"
        )

    if metric and metric not in df.columns:
        raise ValueError(
            f"指标字段不存在：{metric}。"
            f"可用字段：{list(df.columns)}"
        )


def build_grouped_data(
    df: pd.DataFrame,
    dimension: str,
    metric: str,
    aggregation: str,
    sort: str,
    top_n: int,
):
    """生成柱状图、折线图、饼图使用的聚合表。"""

    working_df = df.copy()

    working_df[dimension] = (
        normalize_category(
            working_df[dimension]
        )
    )

    before_rows = len(working_df)

    if aggregation == "count":
        working_df = working_df.dropna(
            subset=[dimension]
        )

        result = (
            working_df.groupby(
                dimension,
                dropna=False,
            )
            .size()
            .reset_index(name="数量")
        )

        value_column = "数量"

    else:
        working_df[metric] = (
            convert_numeric(
                working_df[metric]
            )
        )

        valid_rate = (
            working_df[metric]
            .notna()
            .mean()
        )

        if valid_rate < 0.5:
            raise ValueError(
                f"字段“{metric}”只有"
                f"{valid_rate:.1%}的数据能够转换为数值，"
                "不适合作为当前统计指标。"
            )

        working_df = working_df.dropna(
            subset=[
                dimension,
                metric,
            ]
        )

        result = (
            working_df.groupby(
                dimension,
                as_index=False,
            )[metric]
            .agg(aggregation)
        )

        value_column = metric

    removed_rows = (
        before_rows - len(working_df)
    )

    # 尝试识别日期横轴
    parsed_date = pd.to_datetime(
        result[dimension],
        errors="coerce",
    )

    is_date_dimension = (
        len(result) > 0
        and parsed_date.notna().mean() >= 0.8
    )

    if is_date_dimension:
        result["_parsed_date"] = parsed_date
        result = result.sort_values(
            "_parsed_date"
        )
        result = result.drop(
            columns=["_parsed_date"]
        )

    elif sort != "none":
        result = result.sort_values(
            value_column,
            ascending=(
                sort == "ascending"
            ),
        )

    if top_n and top_n > 0:
        result = result.head(
            min(top_n, 50)
        )

    result = result.reset_index(
        drop=True
    )

    metadata = {
        "source_rows": int(
            len(df)
        ),
        "valid_rows": int(
            len(working_df)
        ),
        "removed_rows": int(
            removed_rows
        ),
        "result_rows": int(
            len(result)
        ),
        "date_dimension": bool(
            is_date_dimension
        ),
    }

    return (
        result,
        value_column,
        metadata,
    )


def build_scatter_data(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    top_n: int,
):
    """生成散点图数据。"""

    working_df = df[
        [x_column, y_column]
    ].copy()

    working_df[x_column] = (
        convert_numeric(
            working_df[x_column]
        )
    )

    working_df[y_column] = (
        convert_numeric(
            working_df[y_column]
        )
    )

    before_rows = len(working_df)

    working_df = working_df.dropna()

    if len(working_df) == 0:
        raise ValueError(
            "两个字段没有可以用于散点图的数值数据"
        )

    if top_n and top_n > 0:
        # 散点图限制数据量，但不代表 Top 排名
        working_df = working_df.head(
            min(top_n, 500)
        )

    metadata = {
        "source_rows": int(len(df)),
        "valid_rows": int(
            len(working_df)
        ),
        "removed_rows": int(
            before_rows - len(working_df)
        ),
        "result_rows": int(
            len(working_df)
        ),
    }

    return (
        working_df.reset_index(
            drop=True
        ),
        metadata,
    )


def build_hist_data(
    df: pd.DataFrame,
    column: str,
):
    """生成直方图数据。"""

    numeric_data = convert_numeric(
        df[column]
    ).dropna()

    if numeric_data.empty:
        raise ValueError(
            f"字段“{column}”没有可用于直方图的数值"
        )

    metadata = {
        "source_rows": int(len(df)),
        "valid_rows": int(
            len(numeric_data)
        ),
        "removed_rows": int(
            len(df) - len(numeric_data)
        ),
        "result_rows": int(
            len(numeric_data)
        ),
    }

    return numeric_data, metadata


def save_figure(
    figure,
) -> Path:
    """将 Plotly 图表保存为 JSON。"""

    chart_id = uuid.uuid4().hex

    chart_path = (
        CHART_DIR /
        f"chart_{chart_id}.json"
    )

    chart_path.write_text(
        figure.to_json(),
        encoding="utf-8",
    )

    return chart_path


@tool
def make_chart(
    csv_path: str,
    chart_type: ChartType,
    dimension: str,
    metric: str = "",
    aggregation: AggregationType = "sum",
    sort: SortType = "descending",
    top_n: int = 10,
    title: str = "",
) -> str:
    """
    根据 CSV 生成经过验证的交互图表。

    参数说明：

    csv_path：
    当前 CSV 文件路径。

    chart_type：
    bar 柱状图；
    line 折线图；
    pie 饼图；
    scatter 散点图；
    hist 直方图。

    dimension：
    分类字段、横轴字段或直方图字段。

    metric：
    数值指标或散点图纵轴字段。
    aggregation=count 时可以为空。

    aggregation：
    sum 总和；
    mean 平均值；
    count 数量；
    min 最小值；
    max 最大值；
    median 中位数。

    sort：
    ascending 升序；
    descending 降序；
    none 不排序。

    top_n：
    最多显示多少项，最大 50。
    时间折线图一般设置为 50。

    title：
    图表中文标题。

    必须先准确判断维度、指标和聚合方式。
    不确定字段时先调用 read_csv。
    """

    if not Path(csv_path).is_file():
        return json.dumps(
            {
                "success": False,
                "error": "CSV 文件不存在",
            },
            ensure_ascii=False,
        )

    if top_n < 1:
        top_n = 10

    top_n = min(top_n, 50)

    try:
        df = read_csv_safely(
            csv_path
        )

        if df.empty:
            raise ValueError(
                "CSV 文件没有数据"
            )

        validate_columns(
            df=df,
            dimension=dimension,
            metric=metric,
            aggregation=aggregation,
            chart_type=chart_type,
        )

        chart_title = (
            title.strip()
            if title.strip()
            else f"{dimension}分析"
        )

        color_sequence = [
            "#B9D857",
            "#789325",
            "#D8E99D",
            "#252A22",
            "#7A8374",
        ]

        if chart_type in (
            "bar",
            "line",
            "pie",
        ):
            (
                chart_data,
                value_column,
                metadata,
            ) = build_grouped_data(
                df=df,
                dimension=dimension,
                metric=metric,
                aggregation=aggregation,
                sort=sort,
                top_n=top_n,
            )

            if chart_data.empty:
                raise ValueError(
                    "清洗和聚合后没有可用数据"
                )

            if (
                chart_type == "pie"
                and len(chart_data) > 8
            ):
                raise ValueError(
                    "饼图最多建议显示 8 个类别，"
                    "请减少 top_n 或改用柱状图"
                )

            if chart_type == "bar":
                figure = px.bar(
                    chart_data,
                    x=dimension,
                    y=value_column,
                    title=chart_title,
                    text_auto=".4s",
                    color_discrete_sequence=(
                        color_sequence
                    ),
                )

            elif chart_type == "line":
                figure = px.line(
                    chart_data,
                    x=dimension,
                    y=value_column,
                    title=chart_title,
                    markers=True,
                    color_discrete_sequence=(
                        color_sequence
                    ),
                )

            else:
                figure = px.pie(
                    chart_data,
                    names=dimension,
                    values=value_column,
                    title=chart_title,
                    hole=0.35,
                    color_discrete_sequence=(
                        color_sequence
                    ),
                )

        elif chart_type == "scatter":
            (
                chart_data,
                metadata,
            ) = build_scatter_data(
                df=df,
                x_column=dimension,
                y_column=metric,
                top_n=min(
                    top_n * 20,
                    500,
                ),
            )

            value_column = metric

            figure = px.scatter(
                chart_data,
                x=dimension,
                y=metric,
                title=chart_title,
                color_discrete_sequence=(
                    color_sequence
                ),
                opacity=0.75,
            )

        else:
            (
                numeric_data,
                metadata,
            ) = build_hist_data(
                df=df,
                column=dimension,
            )

            chart_data = pd.DataFrame({
                dimension: numeric_data
            })

            value_column = dimension

            figure = px.histogram(
                chart_data,
                x=dimension,
                nbins=20,
                title=chart_title,
                color_discrete_sequence=(
                    color_sequence
                ),
            )

        figure.update_layout(
            template="plotly_white",
            title={
                "x": 0.02,
                "xanchor": "left",
            },
            margin={
                "l": 45,
                "r": 30,
                "t": 70,
                "b": 50,
            },
            hovermode="closest",
            font={
                "family": (
                    "Microsoft YaHei, Arial"
                ),
            },
        )

        if chart_type == "bar":
            figure.update_traces(
                marker_color="#82A5D9",
                marker_line_color="#252A22",
                marker_line_width=0.5,
            )

        chart_path = save_figure(
            figure
        )

        preview = (
            chart_data.head(20)
            .where(
                pd.notna(chart_data),
                None,
            )
            .to_dict(orient="records")
        )

        chart_state = {
            "chart_type": chart_type,
            "dimension": dimension,
            "metric": metric,
            "aggregation": aggregation,
            "sort": sort,
            "top_n": top_n,
            "title": chart_title,
        }

        result = {
            "success": True,
            "chart_path": str(
                chart_path
            ),
            "chart_state": chart_state,
            "value_column": value_column,
            "metadata": metadata,
            "preview": preview,
        }

        return json.dumps(
            result,
            ensure_ascii=False,
            default=str,
        )

    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "available_columns": list(
                    df.columns
                ) if "df" in locals() else [],
            },
            ensure_ascii=False,
        )