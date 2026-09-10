import json
from pathlib import Path

from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from fastapi.responses import (
    StreamingResponse,
)
from fastapi.staticfiles import (
    StaticFiles,
)
from pydantic import BaseModel

import agent


BASE_DIR = Path(__file__).resolve().parent
CHART_DIR = BASE_DIR / "charts"
CHART_DIR.mkdir(exist_ok=True)


app = FastAPI(
    title="聊天与数据分析 Agent API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/charts",
    StaticFiles(
        directory=str(CHART_DIR)
    ),
    name="charts",
)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    data_mode: bool = False
    csv_path: str = ""


class ClearRequest(BaseModel):
    session_id: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "chat-data-agent",
    }


@app.post("/chat/stream")
def chat_stream_endpoint(
    request: ChatRequest,
):
    """
    NDJSON 流式接口。

    delta 表示一小段回答；
    final 表示本次请求结束；
    error 表示运行出错。
    """

    def event_generator():
        try:
            for event in agent.chat_stream(
                session_id=(
                    request.session_id
                ),
                user_input=(
                    request.message
                ),
                data_mode=(
                    request.data_mode
                ),
                csv_path=(
                    request.csv_path
                ),
            ):
                # agent 返回的是本地文件路径，
                # API 需要转换成浏览器访问地址。
                if event.get(
                    "type"
                ) == "final":
                    event["charts"] = [
                        (
                            f"/charts/"
                            f"{Path(path).name}"
                        )
                        for path in event.get(
                            "charts",
                            [],
                        )
                    ]

                yield (
                    json.dumps(
                        event,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        except Exception as error:
            print(
                "Agent 流式运行错误：",
                repr(error),
            )

            yield (
                json.dumps(
                    {
                        "type": "error",
                        "message": str(error),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type=(
            "application/x-ndjson"
        ),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/clear")
def clear_endpoint(
    request: ClearRequest,
):
    agent.clear_session(
        session_id=request.session_id,
    )

    return {
        "success": True,
        "message": "会话已清空",
    }