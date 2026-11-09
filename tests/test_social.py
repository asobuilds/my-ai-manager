"""Tests for the social media management API endpoints."""
from uuid import uuid4

from fastapi.testclient import TestClient


class TestSocialPosts:
    def test_list_posts_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/social/posts", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_post(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/social/posts",
            json={
                "platform": "X",
                "content": "Check out our fresh apples!",
                "status": "draft",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["platform"] == "X"
        assert data["content"] == "Check out our fresh apples!"
        assert data["status"] == "draft"
        assert "id" in data

    def test_update_post(self, client: TestClient, auth_headers):
        create = client.post(
            "/api/v1/social/posts",
            json={
                "platform": "Instagram",
                "content": "Organic bananas on sale!",
                "status": "draft",
            },
            headers=auth_headers,
        )
        post_id = create.json()["id"]

        resp = client.patch(
            f"/api/v1/social/posts/{post_id}",
            json={"status": "published"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "published"
        assert data["content"] == "Organic bananas on sale!"

    def test_update_post_not_found(self, client: TestClient, auth_headers):
        fake_id = str(uuid4())
        resp = client.patch(
            f"/api/v1/social/posts/{fake_id}",
            json={"status": "published"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_generate_post(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/social/generate",
            json={"product_name": "Organic Milk", "platform": "X"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert "Organic Milk" in data["content"] or "Supermarket" in data["content"]
        assert data["platform"] == "X"
