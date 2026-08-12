"""Thin client for the Ollama OpenAI-compatible chat endpoint.

Returns the visible answer (`content`), the separated chain-of-thought
(`reasoning`, when a reasoning model exposes it), token usage, and latency.
Reasoning text is captured for auditing but is NOT used for scoring; scoring
uses only the visible `content`, exactly as a downstream application would.
"""
from __future__ import annotations
import time
import requests
from config import ENDPOINT, GEN, REQUEST_TIMEOUT, MAX_RETRIES


def chat(model_tag: str, user_prompt: str, system_prompt: str | None = None) -> dict:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    payload = {"model": model_tag, "messages": messages, **GEN}

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            t0 = time.time()
            r = requests.post(ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT)
            dt = time.time() - t0
            r.raise_for_status()
            d = r.json()
            msg = d["choices"][0]["message"]
            return {
                "content": (msg.get("content") or "").strip(),
                "reasoning": (msg.get("reasoning") or "").strip(),
                "finish_reason": d["choices"][0].get("finish_reason"),
                "usage": d.get("usage", {}),
                "latency_s": round(dt, 2),
                "error": None,
            }
        except Exception as e:  # noqa: BLE001 - we want to retry on any transport error
            last_err = str(e)
            time.sleep(2 * attempt)
    return {"content": "", "reasoning": "", "finish_reason": "error",
            "usage": {}, "latency_s": None, "error": last_err}
