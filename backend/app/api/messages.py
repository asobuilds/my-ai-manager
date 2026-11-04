"""Messages API endpoints — sync, list, and draft reply."""
from __future__ import annotations

import json
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.integrations.mock_gmail import MockGmailConnector
from app.models.models import Message, User
from app.services.ingestion import sync_messages_for_user

# ruff: noqa: B008

router = APIRouter(prefix="/messages", tags=["messages"])
settings = get_settings()


class DraftRequest(BaseModel):
    message_id: str


class SendDraftRequest(BaseModel):
    message_id: str
    draft_text: str


@router.post("/draft")
async def draft_reply(
    body: DraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an AI draft reply for a specific message using Agnes AI."""
    msg = db.query(Message).filter(
        Message.id == UUID(body.message_id),
        Message.user_id == current_user.id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    system_prompt = (
        "You are Aso, a personal AI assistant. Never identify as Agnes or an LLM. "
        "Always refer to yourself as Aso. "
        "Generate a professional, concise email reply to the message below. "
        "Output ONLY the reply text — no greetings like 'Here is a draft' or explanations."
    )
    user_prompt = (
        f"Subject: {getattr(msg, 'subject', None) or '(no subject)'}\n"
        f"From: {msg.sender or '(unknown sender)'}\n"
        f"Received: {msg.received_at.isoformat() if msg.received_at else '(no date)'}\n"
        f"Content:\n{msg.content or '(no content)'}"
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
    draft_text = choices[0].get("message", {}).get("content", "")

    return {"draft": draft_text}


@router.post("/send")
def send_draft(
    body: SendDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a message as replied after sending the draft."""
    msg = db.query(Message).filter(
        Message.id == UUID(body.message_id),
        Message.user_id == current_user.id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.status = "replied"
    db.commit()
    return {"status": "success"}


@router.post("/sync")
def sync_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sync messages from connected platforms into the database."""
    connector = MockGmailConnector()
    synced = sync_messages_for_user(current_user.id, connector, db)
    return {"synced": synced}


@router.get("")
def list_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's messages ordered by priority descending."""
    messages = (
        db.query(Message)
        .filter(Message.user_id == current_user.id)
        .order_by(Message.priority_score.desc(), Message.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(m.id),
            "platform": m.platform,
            "external_id": m.external_id,
            "sender": m.sender,
            "content": m.content,
            "received_at": m.received_at.isoformat() if m.received_at else None,
            "priority_score": m.priority_score,
            "category": m.category,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]
