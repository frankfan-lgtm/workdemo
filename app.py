"""
即梦 AI 创作助手 - 搜索 Agent Demo
主入口：FastAPI 服务
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.intent import analyze_intent
from agent.router import route_and_search

app = FastAPI(title="即梦 AI 创作助手")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatRequest(BaseModel):
    message: str
    context: str = ""


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = BASE_DIR / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    主聊天接口
    1. 分析意图
    2. 路由搜索
    3. 返回结果
    """
    # Step 1: 意图分析（async，支持 LLM 调用）
    intent = await analyze_intent(req.message, req.context)

    if not intent.need_search:
        return {
            "need_search": False,
            "reasoning": intent.reasoning,
        }

    # Step 2: 路由搜索
    aggregated = await route_and_search(intent)

    # Step 3: 序列化返回
    results_by_source = {}
    for source_key, items in aggregated.results_by_source.items():
        results_by_source[source_key] = [asdict(item) for item in items]

    return {
        "need_search": True,
        "intent": {
            "creative_intent": intent.creative_intent.value,
            "search_sources": [s.value for s in intent.search_sources],
            "reasoning": intent.reasoning,
        },
        "results_by_source": results_by_source,
        "summary": aggregated.summary,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
