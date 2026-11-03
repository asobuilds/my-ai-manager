"""Messages API endpoints — sync and list."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.integrations.mock_gmail import MockGmailConnector
from app.models.models import Message, User
from app.services.ingestion import sync_messages_for_user

# ruff: noqa: B008

router = APIRouter(prefix="/messages", tags=["messages"])


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
