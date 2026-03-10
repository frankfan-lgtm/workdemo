"""
火山方舟 API 客户端
使用 Responses API 格式，支持 web_search 等内置工具
"""
from __future__ import annotations

import json
import os
from typing import Optional, List

import httpx

ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_MODEL = os.getenv("ARK_MODEL", "deepseek-v3-2-251201")

_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=60.0)
    return _client


async def chat_completion(
    messages: list[dict],
    tools: Optional[List[dict]] = None,
    temperature: float = 0.3,
) -> dict:
    """
    调用火山方舟 Responses API

    Args:
        messages: [{"role": "user", "content": [{"type": "input_text", "text": "..."}]}]
        tools: 可选工具列表，如 [{"type": "web_search", "max_keyword": 3}]
        temperature: 温度参数

    Returns:
        API 响应的 JSON
    """
    client = _get_client()

    payload = {
        "model": ARK_MODEL,
        "stream": False,
        "temperature": temperature,
        "input": messages,
    }
    if tools:
        payload["tools"] = tools

    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = await client.post(
        f"{ARK_BASE_URL}/responses",
        json=payload,
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def extract_text_from_response(response: dict) -> str:
    """从 Responses API 返回值中提取文本内容"""
    output = response.get("output", [])
    texts = []
    for item in output:
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    texts.append(content["text"])
    return "\n".join(texts)


def extract_json_from_response(response: dict) -> Optional[dict]:
    """从 Responses API 返回值中提取 JSON 对象"""
    text = extract_text_from_response(response)
    # 尝试从 markdown code block 中提取
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        return None
