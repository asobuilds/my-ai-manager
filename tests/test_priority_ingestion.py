"""Tests for priority engine and ingestion service."""

from app.integrations.base_connector import BaseConnector
from app.models.models import Message
from app.services.ingestion import sync_messages_for_user
from app.services.priority_engine import calculate_priority

# ── Priority engine tests ────────────────────────────────────

class TestPriorityEngine:
    def test_work_priority(self):
        result = calculate_priority({"sender": "boss@company.com", "content": "urgent meeting"})
        assert result["priority_score"] == 10
        assert result["category"] == "Work"

    def test_newsletter_priority(self):
        result = calculate_priority({"sender": "news@site.com", "content": "weekly digest unsubscribe"})
        assert result["priority_score"] == 1
        assert result["category"] == "Newsletter"

    def test_spam_priority(self):
        result = calculate_priority({"sender": "spam@evil.com", "content": "you won a prize"})
        assert result["priority_score"] >= 0
        assert result["category"] == "Spam"

    def test_job_priority(self):
        result = calculate_priority({"sender": "recruiting@board.com", "content": "new job opening"})
        assert result["priority_score"] == 8
        assert result["category"] == "Job"

    def test_combined_keywords(self):
        result = calculate_priority({"sender": "client@work.com", "content": "job interview"})
        assert result["priority_score"] == 10
        assert result["category"] == "Work"

    def test_no_keywords(self):
        result = calculate_priority({"sender": "friend@example.com", "content": "hello there"})
        assert result["priority_score"] == 0
        assert result["category"] == "Other"


# ── Ingestion service tests ──────────────────────────────────

class FakeGmailConnector(BaseConnector):
    platform = "gmail"

    def __init__(self, messages: list[dict]):
        self._messages = messages

    def fetch_messages(self) -> list[dict]:
        return self._messages

    def send_reply(self, external_id: str, text: str) -> bool:
        return True


class TestIngestion:
    def test_sync_inserts_messages(self, db_session):
        from app.core.security import hash_password
        from app.models.models import User

        user = User(email="sync@test.com", hashed_password=hash_password("testpass123"))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connector = FakeGmailConnector([
            {"external_id": "msg-1", "sender": "a@b.com", "content": "hello"},
            {"external_id": "msg-2", "sender": "boss@work.com", "content": "meeting"},
        ])

        inserted = sync_messages_for_user(user.id, connector, db_session)
        assert inserted == 2

        messages = db_session.query(Message).filter(Message.user_id == user.id).all()
        assert len(messages) == 2
        assert messages[0].platform == "gmail"
        assert messages[1].priority_score == 10
        assert messages[1].category == "Work"

    def test_sync_skips_duplicates(self, db_session):
        from app.core.security import hash_password
        from app.models.models import User

        user = User(email="dup@test.com", hashed_password=hash_password("testpass123"))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connector = FakeGmailConnector([
            {"external_id": "msg-1", "sender": "a@b.com", "content": "hello"},
        ])

        sync_messages_for_user(user.id, connector, db_session)
        sync_messages_for_user(user.id, connector, db_session)

        count = db_session.query(Message).filter(Message.user_id == user.id).count()
        assert count == 1

    def test_sync_empty(self, db_session):
        from app.core.security import hash_password
        from app.models.models import User

        user = User(email="empty@test.com", hashed_password=hash_password("testpass123"))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connector = FakeGmailConnector([])
        inserted = sync_messages_for_user(user.id, connector, db_session)
        assert inserted == 0
