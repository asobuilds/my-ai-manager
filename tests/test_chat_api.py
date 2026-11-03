"""Tests for the mock chat endpoint."""
from app.models.models import Message


class TestChatApi:
    def test_chat_generic(self, client, auth_headers):
        resp = client.post("/api/v1/chat", json={"message": "Hello there"}, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"] == "Hello! I am your AI assistant. How can I help you manage your emails today?"
        assert data["conversation_id"] is None

    def test_chat_unread_empty(self, client, auth_headers):
        resp = client.post("/api/v1/chat", json={"message": "Show me unread"}, headers=auth_headers)
        assert resp.status_code == 200
        assert "0 unread messages" in resp.json()["response"]

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

        resp = client.post("/api/v1/chat", json={"message": "Any unread?"}, headers=auth_headers)
        assert resp.status_code == 200
        assert "1 unread messages" in resp.json()["response"]
        assert "boss@company.com" in resp.json()["response"]

    def test_chat_reply(self, client, auth_headers):
        resp = client.post("/api/v1/chat", json={"message": "Draft a reply"}, headers=auth_headers)
        assert resp.status_code == 200
        assert "Sure boss, I will review the report tonight." in resp.json()["response"]

    def test_chat_unauthenticated(self, client):
        resp = client.post("/api/v1/chat", json={"message": "hi"})
        assert resp.status_code == 401
