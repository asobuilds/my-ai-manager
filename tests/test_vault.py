"""Tests for the secure vault (encrypted file storage) endpoints."""
from fastapi.testclient import TestClient


def _upload(client, headers, filename="report.txt", content=b"hello vault", password="secret123"):
    return client.post(
        "/api/v1/vault/upload",
        files={"file": (filename, content, "text/plain")},
        data={"password": password},
        headers=headers,
    )


class TestVaultUpload:
    def test_upload_returns_metadata(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        resp = _upload(client, auth_headers)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["filename"] == "report.txt"
        assert data["id"] is not None
        assert data["user_id"] is not None
        assert data["encrypted_path"] != ""
        assert data["created_at"] is not None

    def test_upload_file_is_encrypted_on_disk(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        original = b"super-secret-bytes"
        data = _upload(client, auth_headers, content=original).json()
        on_disk = open(data["encrypted_path"], "rb").read()
        assert on_disk != original
        assert b"super-secret-bytes" not in on_disk

    def test_upload_requires_password(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        # Empty password is rejected by validation.
        resp = client.post(
            "/api/v1/vault/upload",
            files={"file": ("a.txt", b"data", "text/plain")},
            data={"password": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        # Missing password entirely is also rejected.
        resp = client.post(
            "/api/v1/vault/upload",
            files={"file": ("a.txt", b"data", "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_upload_unauthenticated(self, client: TestClient, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        resp = client.post(
            "/api/v1/vault/upload",
            files={"file": ("a.txt", b"data", "text/plain")},
            data={"password": "secret123"},
        )
        assert resp.status_code == 401


class TestVaultList:
    def test_list_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/vault/files", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_uploaded_files(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        _upload(client, auth_headers, filename="one.txt")
        _upload(client, auth_headers, filename="two.txt")
        resp = client.get("/api/v1/vault/files", headers=auth_headers)
        assert resp.status_code == 200
        assert [f["filename"] for f in resp.json()] == ["two.txt", "one.txt"]

    def test_list_is_user_scoped(self, client: TestClient, db_session, tmp_path, monkeypatch):
        from app.core.security import hash_password
        from app.models.models import User

        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        user_a = User(email="a@example.com", hashed_password=hash_password("passApass1"), role="owner")
        user_b = User(email="b@example.com", hashed_password=hash_password("passBpass1"), role="owner")
        db_session.add_all([user_a, user_b])
        db_session.commit()
        db_session.refresh(user_a)
        db_session.refresh(user_b)

        headers_a = {
            "Authorization": f"Bearer {client.post('/api/v1/auth/login', json={'email': 'a@example.com', 'password': 'passApass1'}).json()['access_token']}"
        }
        headers_b = {
            "Authorization": f"Bearer {client.post('/api/v1/auth/login', json={'email': 'b@example.com', 'password': 'passBpass1'}).json()['access_token']}"
        }

        _upload(client, headers_a, filename="mine.txt")

        list_a = client.get("/api/v1/vault/files", headers=headers_a).json()
        list_b = client.get("/api/v1/vault/files", headers=headers_b).json()
        assert [f["filename"] for f in list_a] == ["mine.txt"]
        assert list_b == []

    def test_list_unauthenticated(self, client: TestClient):
        assert client.get("/api/v1/vault/files").status_code == 401


class TestVaultDownload:
    def test_download_with_correct_password(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        original = b"decrypt me please"
        fid = _upload(client, auth_headers, content=original, password="correctpw").json()["id"]

        resp = client.post(f"/api/v1/vault/download/{fid}", json={"password": "correctpw"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.content == original
        assert 'filename="report.txt"' in resp.headers.get("content-disposition", "")

    def test_download_with_wrong_password(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        fid = _upload(client, auth_headers, password="correctpw").json()["id"]

        resp = client.post(f"/api/v1/vault/download/{fid}", json={"password": "wrong"}, headers=auth_headers)
        assert resp.status_code == 400

    def test_download_not_found(self, client: TestClient, auth_headers, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        resp = client.post(
            "/api/v1/vault/download/00000000-0000-0000-0000-000000000000",
            json={"password": "x"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_download_scoped_to_owner(self, client: TestClient, db_session, tmp_path, monkeypatch):
        from app.core.security import hash_password
        from app.models.models import User

        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        user_a = User(email="a@example.com", hashed_password=hash_password("passApass1"), role="owner")
        user_b = User(email="b@example.com", hashed_password=hash_password("passBpass1"), role="owner")
        db_session.add_all([user_a, user_b])
        db_session.commit()

        headers_a = {
            "Authorization": f"Bearer {client.post('/api/v1/auth/login', json={'email': 'a@example.com', 'password': 'passApass1'}).json()['access_token']}"
        }
        headers_b = {
            "Authorization": f"Bearer {client.post('/api/v1/auth/login', json={'email': 'b@example.com', 'password': 'passBpass1'}).json()['access_token']}"
        }

        fid = _upload(client, headers_a, password="pw").json()["id"]

        # Owner can download; other user cannot.
        assert client.post(f"/api/v1/vault/download/{fid}", json={"password": "pw"}, headers=headers_a).status_code == 200
        assert client.post(f"/api/v1/vault/download/{fid}", json={"password": "pw"}, headers=headers_b).status_code == 404

    def test_download_unauthenticated(self, client: TestClient, tmp_path, monkeypatch):
        monkeypatch.setattr("app.api.vault.VAULT_DIR", str(tmp_path))
        resp = client.post(
            "/api/v1/vault/download/00000000-0000-0000-0000-000000000000",
            json={"password": "x"},
        )
        assert resp.status_code == 401
