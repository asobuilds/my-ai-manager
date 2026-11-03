"""Chat endpoint using the Agnes AI API."""
from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Message, User
from app.schemas.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


@router.post("")
@router.post("/")
async def chat(body: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Forward the user's message to Agnes AI with inbox context."""
    unread_messages = (
        db.query(Message)
        .filter(Message.user_id == current_user.id, Message.status == "unread")
        .all()
    )
    inbox_context: list[dict[str, Any]] = [
        {
            "sender": m.sender,
            "subject": getattr(m, "subject", None),
            "content": m.content,
            "received_at": m.received_at.isoformat() if m.received_at else None,
            "priority_score": m.priority_score,
            "category": m.category,
        }
        for m in unread_messages
    ]

    system_prompt_parts = [
        "You are a helpful AI assistant that helps manage emails and messages.",
    ]
    if inbox_context:
        system_prompt_parts.append(
            f"Current unread messages in the user's inbox:\n{json.dumps(inbox_context, default=str)}"
        )
    else:
        system_prompt_parts.append("The user has no unread messages.")

    base_url = settings.AGNES_BASE_URL.rstrip("/")
    url = base_url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": "\n".join(system_prompt_parts)},
            {"role": "user", "content": body.message},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI API error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI request failed: {exc}")

    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="No response from Agnes AI")
    message = choices[0].get("message", {})
    response_text = message.get("content", "")

    return {"response": response_text, "conversation_id": body.conversation_id}
