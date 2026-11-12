"""Tests for the user preferences API endpoints."""
from fastapi.testclient import TestClient


class TestPreferences:
    def test_get_preferences_default(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/preferences", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["theme_mode"] == "system"
        assert data["theme_palette"] == "teal"
        assert data["font_size"] == "medium"
        assert isinstance(data["enabled_features"], list)
        assert "dashboard" in data["enabled_features"]

    def test_update_preferences(self, client: TestClient, auth_headers):
        resp = client.patch(
            "/api/v1/preferences",
            json={
                "theme_mode": "dark",
                "theme_palette": "rose",
                "font_size": "large",
                "enabled_features": ["dashboard", "calendar", "shop"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["theme_mode"] == "dark"
        assert data["theme_palette"] == "rose"
        assert data["font_size"] == "large"
        # All required features must always be present
        required = {"dashboard", "chat", "inventory", "shop", "social", "jobs", "calendar", "health", "home", "integrations", "settings", "profile"}
        assert required.issubset(set(data["enabled_features"]))

        # Verify get returns updated values
        get_resp = client.get("/api/v1/preferences", headers=auth_headers)
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["theme_palette"] == "rose"
