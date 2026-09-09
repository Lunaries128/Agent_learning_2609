from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import agent


BASE_DIR = Path(__file__).resolve().parent
CHART_DIR = BASE_DIR / "charts"

CHART_DIR.mkdir(exist_ok=True)


app = FastAPI(
    title="聊天与数据分析Agent API"
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


class ChatResponse(BaseModel):
    reply: str
    data_mode: bool
    images: list[str] = Field(
        default_factory=list
    )


class ClearRequest(BaseModel):
    session_id: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "chat-data-agent",
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat_endpoint(req: ChatRequest):
    try:
        result = agent.chat(
            session_id=req.session_id,
            user_input=req.message,
            data_mode=req.data_mode,
            csv_path=req.csv_path,
        )

        image_urls = [
            f"/charts/{Path(path).name}"
            for path in result["images"]
        ]

        return ChatResponse(
            reply=result["reply"],
            data_mode=result["data_mode"],
            images=image_urls,
        )

    except Exception as error:
        print(
            "Agent运行错误：",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.post("/clear")
def clear_endpoint(req: ClearRequest):
    agent.clear_session(
        session_id=req.session_id,
    )

    return {
        "success": True,
        "message": "会话已清空",
    }