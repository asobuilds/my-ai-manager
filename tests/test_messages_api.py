"""Tests for messages API endpoints."""
from datetime import UTC, datetime
from unittest.mock import patch

from app.integrations.base_connector import BaseConnector
from app.models.models import Message


class FakeGmailConnector(BaseConnector):
    """Mock connector for testing without real Gmail API."""

    platform = "gmail"

    def __init__(self, messages: list[dict]):
        self._messages = messages

    def fetch_messages(self) -> list[dict]:
        return self._messages

    def send_reply(self, external_id: str, text: str) -> bool:
        return True


# ── Sync tests ─────────────────────────────────────────────────

class TestSyncMessages:
    def test_sync_no_google_connection(self, client, auth_headers):
        """Sync works even without a stored Google connection (uses mock connector)."""
        resp = client.post("/api/v1/messages/sync", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["synced"] == 3

    def test_sync_success(self, client, auth_headers, db_session):
        from app.models.models import User, UserConnection

        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None

        conn = UserConnection(
            user_id=user.id,
            provider="google",
            access_token="fake-access",
            refresh_token="fake-refresh",
            is_active=True,
            token_expires_at=datetime.now(tz=UTC),
        )
        db_session.add(conn)
        db_session.commit()

        fake_messages = [
            {"external_id": "m1", "sender": "boss@work.com", "content": "urgent meeting"},
            {"external_id": "m2", "sender": "promo@store.com", "content": "weekly digest unsubscribe"},
            {"external_id": "m3", "sender": "friend@mail.com", "content": "hey there"},
        ]

        with patch("app.api.messages.MockGmailConnector") as MockConnector:
            mock_instance = FakeGmailConnector(fake_messages)
            MockConnector.return_value = mock_instance
            resp = client.post("/api/v1/messages/sync", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["synced"] == 3

        messages = db_session.query(Message).filter(Message.user_id == user.id).all()
        assert len(messages) == 3
        assert messages[0].priority_score == 10
        assert messages[1].priority_score == 1
        assert messages[2].priority_score == 0

    def test_sync_duplicate_skipped(self, client, auth_headers, db_session):
        from app.models.models import User, UserConnection

        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None

        conn = UserConnection(
            user_id=user.id,
            provider="google",
            access_token="fake-access",
            refresh_token="fake-refresh",
            is_active=True,
            token_expires_at=datetime.now(tz=UTC),
        )
        db_session.add(conn)
        db_session.commit()

        fake_messages = [
            {"external_id": "m1", "sender": "a@b.com", "content": "hello"},
        ]

        with patch("app.api.messages.MockGmailConnector") as MockConnector:
            mock_instance = FakeGmailConnector(fake_messages)
            MockConnector.return_value = mock_instance
            client.post("/api/v1/messages/sync", headers=auth_headers)
            resp2 = client.post("/api/v1/messages/sync", headers=auth_headers)

        assert resp2.status_code == 200
        assert resp2.json()["synced"] == 0

        count = db_session.query(Message).filter(Message.user_id == user.id).count()
        assert count == 1


# ── List messages tests ────────────────────────────────────────

class TestListMessages:
    def test_list_empty(self, client, auth_headers):
        resp = client.get("/api/v1/messages", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_messages_ordered_by_priority(self, client, auth_headers, db_session):
        from app.models.models import User

        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None

        low = Message(
            user_id=user.id, platform="gmail", external_id="low",
            sender="promo@mail.com", content="newsletter unsubscribe",
            priority_score=1, category="Newsletter", status="unread",
            received_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        high = Message(
            user_id=user.id, platform="gmail", external_id="high",
            sender="boss@mail.com", content="urgent meeting",
            priority_score=10, category="Work", status="unread",
            received_at=datetime(2024, 1, 2, tzinfo=UTC),
        )
        mid = Message(
            user_id=user.id, platform="gmail", external_id="mid",
            sender="hr@jobs.com", content="job opening",
            priority_score=8, category="Job", status="unread",
            received_at=datetime(2024, 1, 3, tzinfo=UTC),
        )
        db_session.add_all([low, high, mid])
        db_session.commit()

        resp = client.get("/api/v1/messages", headers=auth_headers)
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) == 3
        assert messages[0]["priority_score"] == 10
        assert messages[0]["sender"] == "boss@mail.com"
        assert messages[1]["priority_score"] == 8
        assert messages[2]["priority_score"] == 1

    def test_list_unauthenticated(self, client):
        resp = client.get("/api/v1/messages")
        assert resp.status_code == 401
