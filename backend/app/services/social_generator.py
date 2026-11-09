"""Social Media post generator using LLM."""
from __future__ import annotations

import httpx
from app.core.config import get_settings

settings = get_settings()


async def generate_promo_post(product_name: str, platform: str) -> str:
    """Generate a promotional caption for a supermarket product on a specific platform using LLM."""
    if not settings.AGNES_API_KEY:
        return f"🛒 Special offer on {product_name}! Grab yours today at our supermarket. #Fresh #Supermarket #{platform}"

    system_prompt = (
        "You are an expert social media manager for a local supermarket. "
        "Generate an engaging, punchy promotional social media post for the given product and platform. "
        "Include appropriate emojis, hashtags, and a call to action. "
        "Output ONLY the post text — no introductory or concluding remarks."
    )
    user_prompt = f"Product: {product_name}\nPlatform: {platform}"

    base_url = settings.AGNES_BASE_URL.rstrip("/")
    url = base_url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return f"🛒 Special offer on {product_name}! Grab yours today at our supermarket. #Fresh #Supermarket #{platform}"

    choices = data.get("choices", [])
    if not choices:
        return f"🛒 Special offer on {product_name}! Grab yours today at our supermarket. #Fresh #Supermarket #{platform}"
    return choices[0].get("message", {}).get("content", "").strip()
