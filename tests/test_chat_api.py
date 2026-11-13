"""Tests for the Agnes AI chat endpoint."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.models.models import ChatMessage, Conversation, Message, User


class MockResponse:
    def __init__(self, status_code: int = 200, json_data: dict | None = None):
        self._status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self._status_code >= 400:
            raise Exception(f"HTTP {self._status_code}")


class TestChatApi:
    def test_chat_generic(self, client, auth_headers):
        mock_body = {
            "choices": [{"message": {"content": "Hello! How can I help you?"}}],
        }
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(json_data=mock_body)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post("/api/v1/chat", json={"message": "Hello there"}, headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["response"] == "Hello! How can I help you?"
            assert data["conversation_id"] is not None

    def test_chat_unread_empty(self, client, auth_headers):
        mock_body = {
            "choices": [{"message": {"content": "You have no unread messages."}}],
        }
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(json_data=mock_body)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post("/api/v1/chat", json={"message": "Show me unread"}, headers=auth_headers)
            assert resp.status_code == 200
            assert "no unread messages" in resp.json()["response"].lower()

    def test_chat_unread_with_messages(self, client, auth_headers, db_session):
        from app.models.models import User

        user = db_session.query(User).filter(User.email == "test@example.com").first()
        msg = Message(
            user_id=user.id,
            platform="gmail",
            external_id="msg-unread",
            sender="boss@company.com",
            content="urgent task",
            priority_score=10,
            status="unread",
        )
        db_session.add(msg)
        db_session.commit()

        mock_body = {
            "choices": [{"message": {"content": "You have 1 unread message from boss@company.com"}}],
        }
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(json_data=mock_body)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post("/api/v1/chat", json={"message": "Any unread?"}, headers=auth_headers)
            assert resp.status_code == 200
            assert "boss@company.com" in resp.json()["response"]

    def test_chat_api_failure(self, client, auth_headers):
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(status_code=500)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post("/api/v1/chat", json={"message": "hi"}, headers=auth_headers)
            assert resp.status_code == 502

    def test_chat_no_choices(self, client, auth_headers):
        mock_body = {"choices": []}
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(json_data=mock_body)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post("/api/v1/chat", json={"message": "hi"}, headers=auth_headers)
            assert resp.status_code == 502

    def test_chat_unauthenticated(self, client):
        resp = client.post("/api/v1/chat", json={"message": "hi"})
        assert resp.status_code == 401


class TestChatHistory:
    def test_history_unknown_conversation(self, client, auth_headers):
        resp = client.get(
            "/api/v1/chat/history?conversation_id=does-not-exist",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_history_returns_messages_ordered(self, client, auth_headers, db_session):
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        db_session.add(Conversation(id="convo-abc", user_id=user.id))
        db_session.commit()
        db_session.add(
            ChatMessage(
                conversation_id="convo-abc",
                role="user",
                content="hi there",
                created_at=datetime(2026, 11, 1, 9, 0, 0),
            )
        )
        db_session.add(
            ChatMessage(
                conversation_id="convo-abc",
                role="assistant",
                content="hello!",
                created_at=datetime(2026, 11, 1, 9, 0, 5),
            )
        )
        db_session.commit()

        resp = client.get(
            "/api/v1/chat/history?conversation_id=convo-abc",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert [m["role"] for m in data] == ["user", "assistant"]
        assert [m["content"] for m in data] == ["hi there", "hello!"]
        assert all(m["conversation_id"] == "convo-abc" for m in data)

    def test_history_scoped_to_owner(self, client, auth_headers, db_session):
        other = User(email="other-hist@example.com", hashed_password="placeholder", role="owner")
        db_session.add(other)
        db_session.commit()
        db_session.refresh(other)
        db_session.add(Conversation(id="convo-other", user_id=other.id))
        db_session.add(ChatMessage(conversation_id="convo-other", role="user", content="secret"))
        db_session.commit()

        # test@example.com (auth_headers) cannot read another user's conversation.
        resp = client.get(
            "/api/v1/chat/history?conversation_id=convo-other",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_history_unauthenticated(self, client):
        resp = client.get("/api/v1/chat/history?conversation_id=convo-abc")
        assert resp.status_code == 401
