"""Tests for the Agnes AI chat endpoint."""
from unittest.mock import AsyncMock, patch

from app.models.models import Message


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
