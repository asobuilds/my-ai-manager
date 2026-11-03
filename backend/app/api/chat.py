"""Mock chat endpoint for local development without an LLM."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Message, User
from app.schemas.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
@router.post("/")
async def chat(body: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return mock AI responses based on simple keyword rules."""
    text = body.message.lower()

    if "unread" in text:
        unread = (
            db.query(Message)
            .filter(Message.user_id == current_user.id, Message.status == "unread")
            .all()
        )
        count = len(unread)
        if count == 0:
            summary = "You have 0 unread messages."
        else:
            top = max(unread, key=lambda m: m.priority_score)
            summary = f"You have {count} unread messages. The most important is from {top.sender or 'unknown'}."
        response_text = f"[Mock AI] {summary}"
    elif "reply" in text:
        response_text = "Here is a draft reply: 'Sure boss, I will review the report tonight.'"
    else:
        response_text = "Hello! I am your AI assistant. How can I help you manage your emails today?"

    return {"response": response_text, "conversation_id": body.conversation_id}
