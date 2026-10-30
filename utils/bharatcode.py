"""
BharatCode API wrapper — OpenAI-compatible client
"""
import os
import base64
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BHARATCODE_API_KEY")
BASE_URL = os.getenv("BHARATCODE_BASE_URL", "https://bharatcode.ai/api/model/v1")
MODEL = os.getenv("BHARATCODE_MODEL", "qwen-3.8-27b")

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


async def chat(system: str, user: str, temperature: float = 0.7) -> str:
    """Simple text chat with BharatCode LLM."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


async def vision_chat(system: str, user_text: str, image_bytes: bytes) -> str:
    """Send an image + text to the vision model and get a text response."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            },
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()
