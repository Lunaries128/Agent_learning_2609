import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import agent


os.makedirs("maps", exist_ok=True)


app = FastAPI(
    title="智能旅行规划 Agent API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/maps",
    StaticFiles(directory="maps"),
    name="maps",
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    images: list[str] = Field(
        default_factory=list
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "travel-agent",
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat_endpoint(req: ChatRequest):
    result = agent.chat(
        req.session_id,
        req.message,
    )

    image_urls = [
        image_path.replace(
            "maps",
            "/maps",
            1,
        )
        for image_path in result["images"]
    ]

    return ChatResponse(
        reply=result["reply"],
        images=image_urls,
    )