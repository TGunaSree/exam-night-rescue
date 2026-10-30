"""
BharatCode API wrapper — uses the official /responses endpoint
as documented at https://bharatcode.ai/api/model/v1
"""
import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BHARATCODE_API_KEY")
BASE_URL = os.getenv("BHARATCODE_BASE_URL", "https://bharatcode.ai/api/model/v1")
MODEL = os.getenv("BHARATCODE_MODEL", "qwen-3.8-27b")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


async def chat(system: str, user: str, temperature: float = 0.7) -> str:
    """
    Text-only call using POST /responses (BharatCode Responses API).
    Sends system + user as combined input text.
    """
    input_text = f"{system}\n\n{user}"

    payload = {
        "model": MODEL,
        "input": input_text,
        "store": False,
        "max_output_tokens": 3000,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BASE_URL}/responses",
            headers=HEADERS,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    # Extract text from output array
    return _extract_text(data)


async def vision_chat(system: str, user_text: str, image_bytes: bytes) -> str:
    """
    Vision call — sends image + text using POST /responses.
    BharatCode supports image input in the Responses API.
    """
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": MODEL,
        "store": False,
        "max_output_tokens": 2000,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f"{system}\n\n{user_text}"},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{b64}",
                    },
                ],
            }
        ],
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{BASE_URL}/responses",
            headers=HEADERS,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return _extract_text(data)


def _extract_text(data: dict) -> str:
    """Parse text from the BharatCode /responses output format."""
    # Responses API returns output as a list of content blocks
    output = data.get("output", [])
    for item in output:
        if isinstance(item, dict):
            # item could be {"type": "message", "content": [...]}
            content = item.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "output_text":
                        return block.get("text", "").strip()
            # Or direct output_text
            if item.get("type") == "output_text":
                return item.get("text", "").strip()

    # Fallback: output_text at top level
    if "output_text" in data:
        return data["output_text"].strip()

    # Last resort: raw string output
    return str(data.get("output", "No response"))
