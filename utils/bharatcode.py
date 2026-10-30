"""
AI backend — Google Gemini API (gemini-flash-lite-latest)
Optimized for ultra-fast response times (<5 seconds) and multimodal vision.
"""
import os
import base64
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# gemini-flash-lite-latest provides lightning-fast (<5s) vision & text inference
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
BASE_URL       = "https://generativelanguage.googleapis.com/v1beta/models"

HEADERS = {"Content-Type": "application/json"}


def _url(endpoint: str = "generateContent") -> str:
    return f"{BASE_URL}/{GEMINI_MODEL}:{endpoint}?key={GEMINI_API_KEY}"


async def _post(payload: dict, retries: int = 3) -> dict:
    """POST with automatic retry on 503 or transient network hiccups."""
    for attempt in range(retries):
        async with httpx.AsyncClient(timeout=45) as client:
            try:
                resp = await client.post(_url(), headers=HEADERS, json=payload)
                if resp.status_code == 503 and attempt < retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                raise e
    raise RuntimeError("Service temporarily busy. Please try again.")


async def chat(system: str, user: str, temperature: float = 0.7) -> str:
    """Text-only generation."""
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 3000,
        },
    }
    data = await _post(payload)
    return _extract(data)


async def vision_chat(system: str, user_text: str, image_bytes: bytes) -> str:
    """Vision call — image + text with optimized payload."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_text},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
                ],
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2000},
    }
    data = await _post(payload)
    return _extract(data)


def _extract(data: dict) -> str:
    """Pull text from Gemini response."""
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        return "Sorry, I couldn't generate a response. Please try again."
