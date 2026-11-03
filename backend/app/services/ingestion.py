"""Ingestion service for syncing platform messages into the database."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.integrations.base_connector import BaseConnector
from app.models.models import Message
from app.services.priority_engine import calculate_priority


def sync_messages_for_user(
    user_id: UUID,
    connector: BaseConnector,
    db: Session,
) -> int:
    """Sync messages from a connector into the database for a given user.

    Calls `connector.fetch_messages()`, runs each message through the
    priority engine, and upserts the result into the `messages` table.
    Duplicates are skipped based on (user_id, external_id, platform).

    Args:
        user_id: The user to sync messages for.
        connector: An initialized connector instance.
        db: SQLAlchemy session.

    Returns:
        Number of messages newly inserted.
    """
    messages = connector.fetch_messages()
    inserted = 0

    for msg in messages:
        existing = db.query(Message).filter(
            Message.user_id == user_id,
            Message.external_id == msg["external_id"],
            Message.platform == connector.platform,
        ).first()

        if existing:
            continue

        priority_result = calculate_priority(msg)
        message = Message(
            user_id=user_id,
            platform=connector.platform,
            external_id=msg["external_id"],
            sender=msg.get("sender"),
            content=msg.get("content"),
            received_at=msg.get("received_at"),
            priority_score=priority_result["priority_score"],
            category=priority_result["category"],
            status="unread",
        )
        db.add(message)
        inserted += 1

    db.commit()
    return inserted
