from __future__ import annotations

import os

from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def chat(messages: list[dict], model: str | None = None, temperature: float = 0.3) -> str:
    model = model or os.environ.get("QWEN_MODEL", "qwen-max")
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""
