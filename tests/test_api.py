from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[db_session.__self__.get_db if hasattr(db_session, '__self__') else 'get_db'] = override_get_db
    from app.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient, db_session):
    from app.core.security import hash_password
    from app.models.models import User
    user = User(email="test@example.com", hashed_password=hash_password("testpass123"), full_name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    resp = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ───────────────────────────────────────────────

class TestAuth:
    def test_register(self, client: TestClient):
        resp = client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "securepass123",
            "full_name": "New User",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "access_token" not in data

    def test_register_duplicate_email(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 400

    def test_login_success(self, client: TestClient, db_session):
        from app.core.security import hash_password
        from app.models.models import User
        user = User(email="login@test.com", hashed_password=hash_password("loginpass123"))
        db_session.add(user)
        db_session.commit()
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@test.com",
            "password": "loginpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data

    def test_login_wrong_password(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_me(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_me_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401


# ── Drafts tests ─────────────────────────────────────────────

class TestDrafts:
    def test_list_drafts_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/me/drafts", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_draft(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/me/drafts", json={
            "subject": "Hello",
            "body": "Body text",
            "to": "recipient@example.com",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["subject"] == "Hello"
        assert data["body"] == "Body text"
        assert data["to"] == "recipient@example.com"
        assert data["status"] == "draft"

    def test_update_draft(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/me/drafts", json={
            "subject": "Old",
            "body": "Old body",
        }, headers=auth_headers)
        draft_id = create.json()["id"]
        resp = client.put(f"/api/v1/me/drafts/{draft_id}", json={
            "subject": "New Subject",
            "status": "sent",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["subject"] == "New Subject"
        assert data["status"] == "sent"

    def test_delete_draft(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/me/drafts", json={
            "subject": "To delete",
            "body": "Body",
        }, headers=auth_headers)
        draft_id = create.json()["id"]
        resp = client.delete(f"/api/v1/me/drafts/{draft_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp2 = client.get("/api/v1/me/drafts", headers=auth_headers)
        assert len(resp2.json()) == 0

    def test_delete_draft_not_found(self, client: TestClient, auth_headers):
        fake_id = str(uuid4())
        resp = client.delete(f"/api/v1/me/drafts/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404


# ── Job Applications tests ───────────────────────────────────

class TestJobApplications:
    def test_list_jobs_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/me/jobs", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_job(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/me/jobs", json={
            "company": "Acme Corp",
            "position": "Software Engineer",
            "job_url": "https://acme.com/jobs/1",
            "status": "saved",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["company"] == "Acme Corp"
        assert data["status"] == "saved"

    def test_update_job_status(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/me/jobs", json={
            "company": "Acme Corp",
            "position": "Engineer",
        }, headers=auth_headers)
        job_id = create.json()["id"]
        resp = client.put(f"/api/v1/me/jobs/{job_id}", json={
            "status": "applied",
            "notes": "Applied via web",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "applied"

    def test_delete_job(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/me/jobs", json={
            "company": "Acme",
            "position": "Dev",
        }, headers=auth_headers)
        job_id = create.json()["id"]
        resp = client.delete(f"/api/v1/me/jobs/{job_id}", headers=auth_headers)
        assert resp.status_code == 204


# ── File Catalog tests ───────────────────────────────────────

class TestFileCatalog:
    def test_list_files_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/me/files", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_file(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/me/files", json={
            "name": "resume.pdf",
            "path": "/docs/resume.pdf",
            "file_type": "application/pdf",
            "tags": ["resume", "career"],
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "resume.pdf"
        assert data["tags"] == ["resume", "career"]

    def test_delete_file(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/me/files", json={
            "name": "doc.txt",
            "path": "/docs/doc.txt",
        }, headers=auth_headers)
        file_id = create.json()["id"]
        resp = client.delete(f"/api/v1/me/files/{file_id}", headers=auth_headers)
        assert resp.status_code == 204


# ── Connections tests ────────────────────────────────────────

class TestConnections:
    def test_list_connections_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/me/connections", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_connection(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/me/connections", json={
            "provider": "gmail",
            "access_token": "fake-token-123",
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["provider"] == "gmail"

    def test_create_duplicate_connection(self, client: TestClient, auth_headers):
        client.post("/api/v1/me/connections", json={
            "provider": "gmail",
            "access_token": "token-1",
        }, headers=auth_headers)
        resp = client.post("/api/v1/me/connections", json={
            "provider": "gmail",
            "access_token": "token-2",
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_delete_connection(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/me/connections", json={
            "provider": "gmail",
            "access_token": "tok",
        }, headers=auth_headers)
        conn_id = create.json()["id"]
        resp = client.delete(f"/api/v1/me/connections/{conn_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp2 = client.get("/api/v1/me/connections", headers=auth_headers)
        assert resp2.json() == []


# ── Chat tests ───────────────────────────────────────────────

class TestChat:
    def test_chat(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/chat/", json={
            "message": "What drafts do I have?",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "conversation_id" in data

    def test_chat_with_context(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/chat/", json={
            "message": "Summarize my jobs",
            "context_keys": ["gmail", "jobs"],
        }, headers=auth_headers)
        assert resp.status_code == 200


# ── Health ───────────────────────────────────────────────────

class TestHealth:
    def test_health(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ── Google OAuth tests ───────────────────────────────────────

class TestGoogleOAuth:
    def test_google_login_returns_url(self, client: TestClient, auth_headers, monkeypatch):
        import app.api.connections as conn_module

        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_ID", "fake-client-id")
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_SECRET", "fake-secret")
        monkeypatch.setattr(
            conn_module.settings,
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connections/google/callback",
        )

        original = conn_module.generate_authorization_url

        def fake_generate(*args, **kwargs):
            return "https://accounts.google.com/o/oauth2/auth?fake=true"

        conn_module.generate_authorization_url = fake_generate
        try:
            resp = client.get("/api/v1/connections/google/login", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert "authorization_url" in data
            assert "fake=true" in data["authorization_url"]
        finally:
            conn_module.generate_authorization_url = original

    def test_google_login_missing_credentials(self, client: TestClient, auth_headers, monkeypatch):
        import app.api.connections as conn_module
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_ID", "")
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_SECRET", "")
        resp = client.get("/api/v1/connections/google/login", headers=auth_headers)
        assert resp.status_code == 500

    def test_google_callback_unauthenticated(self, client: TestClient, monkeypatch):
        import app.api.connections as conn_module
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_ID", "fake-id")
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_SECRET", "fake-secret")
        monkeypatch.setattr(
            conn_module.settings,
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connections/google/callback",
        )
        resp = client.get(
            "/api/v1/connections/google/callback",
            params={"code": "fake-code", "state": "not-hex"},
        )
        assert resp.status_code == 400

    def test_google_callback_invalid_state(self, client: TestClient, monkeypatch):
        import app.api.connections as conn_module
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_ID", "fake-id")
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_SECRET", "fake-secret")
        monkeypatch.setattr(
            conn_module.settings,
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connections/google/callback",
        )
        resp = client.get(
            "/api/v1/connections/google/callback",
            params={"code": "fake-code", "state": "not-a-valid-hex"},
        )
        assert resp.status_code == 400

    def test_google_callback_user_not_found(self, client: TestClient, monkeypatch, db_session):
        from uuid import uuid4
        import app.api.connections as conn_module
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_ID", "fake-id")
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_SECRET", "fake-secret")
        monkeypatch.setattr(
            conn_module.settings,
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connections/google/callback",
        )
        fake_id = uuid4().hex
        resp = client.get(
            "/api/v1/connections/google/callback",
            params={"code": "fake-code", "state": fake_id},
        )
        assert resp.status_code == 404

    def test_google_callback_success(self, client: TestClient, monkeypatch, db_session, auth_headers):
        from app.models.models import User, UserConnection
        import app.api.connections as conn_module

        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None

        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_ID", "fake-id")
        monkeypatch.setattr(conn_module.settings, "GOOGLE_CLIENT_SECRET", "fake-secret")
        monkeypatch.setattr(
            conn_module.settings,
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connections/google/callback",
        )

        def fake_exchange(*args, **kwargs):
            from datetime import datetime, timezone
            return ("fake-access-token", "fake-refresh-token", datetime.now(tz=timezone.utc))

        original = conn_module.exchange_authorization_code
        conn_module.exchange_authorization_code = fake_exchange
        try:
            resp = client.get(
                "/api/v1/connections/google/callback",
                params={"code": "auth-code-123", "state": user.id.hex},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "connection_id" in data
            assert data["provider"] == "google"
            assert data["is_active"] is True

            conn = db_session.query(UserConnection).filter(
                UserConnection.user_id == user.id,
                UserConnection.provider == "google",
            ).first()
            assert conn is not None
            assert conn.access_token == "fake-access-token"
            assert conn.refresh_token == "fake-refresh-token"
        finally:
            conn_module.exchange_authorization_code = original
