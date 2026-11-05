"""Chat endpoint using the Agnes AI API."""
from __future__ import annotations

import json
import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_owner
from app.models.models import ChatMessage, Conversation, Message, User
from app.schemas.schemas import ChatRequest, ExplainRequest

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


@router.post("")
@router.post("/")
async def chat(body: ChatRequest, current_user: User = Depends(get_current_owner), db: Session = Depends(get_db)):
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

    if not body.conversation_id:
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(id=conversation_id, user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    else:
        conversation_id = body.conversation_id
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    system_prompt_parts = [
        "You are Aso, a personal AI assistant. Never identify as Agnes or an LLM. Always refer to yourself as Aso.",
    ]
    if inbox_context:
        system_prompt_parts.append(
            f"Current unread messages in the user's inbox:\n{json.dumps(inbox_context, default=str)}"
        )
    else:
        system_prompt_parts.append("The user has no unread messages.")

    messages_history: list[dict[str, str]] = [{"role": "system", "content": "\n".join(system_prompt_parts)}]

    if body.conversation_id:
        prior_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        for m in prior_messages:
            messages_history.append({"role": m.role, "content": m.content})

    messages_history.append({"role": "user", "content": body.message})

    user_msg = ChatMessage(conversation_id=conversation_id, role="user", content=body.message)
    db.add(user_msg)
    db.commit()

    base_url = settings.AGNES_BASE_URL.rstrip("/")
    url = base_url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "agnes-2.5-flash",
        "messages": messages_history,
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

    assistant_msg = ChatMessage(conversation_id=conversation_id, role="assistant", content=response_text)
    db.add(assistant_msg)
    db.commit()

    return {"response": response_text, "conversation_id": conversation_id}


@router.post("/explain")
async def explain_draft(
    body: ExplainRequest,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Explain why the AI wrote a specific draft reply, citing the original email."""
    msg = db.query(Message).filter(
        Message.id == uuid.UUID(body.message_id),
        Message.user_id == current_user.id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    system_prompt = (
        "You are Aso, a personal AI assistant. Never identify as Agnes or an LLM. "
        "Always refer to yourself as Aso. "
        "Your job is to explain WHY you wrote a draft reply the way you did. "
        "Reference specific details from the original email to justify your word choices, tone, and structure."
    )
    user_prompt = (
        f"Original email:\n"
        f"  From: {msg.sender or '(unknown)'}\n"
        f"  Subject: {getattr(msg, 'subject', None) or '(no subject)'}\n"
        f"  Content:\n{msg.content or '(no content)'}\n\n"
        f"Draft reply I generated:\n{body.draft_text}\n\n"
        f"Explain in 2-4 sentences why you wrote this draft — what cues from the original email influenced your word choice, tone, and structure?"
    )

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
    except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI API error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI request failed: {exc}")

    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="No response from Agnes AI")
    explanation = choices[0].get("message", {}).get("content", "")

    return {"explanation": explanation}
