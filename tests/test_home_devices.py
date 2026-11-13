"""Tests for the Home Assistant integration service and the /home/devices endpoint."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.services import home_assistant as hass


class FakeHassResponse:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPError(f"simulated HTTP {self.status_code}")


def _configured_settings() -> Settings:
    return Settings(HASS_URL="http://hass.local", HASS_TOKEN="hass-test-token")


class TestGetEntityState:
    def test_not_configured_returns_none(self, monkeypatch):
        monkeypatch.setattr(hass, "settings", Settings())
        assert hass.get_entity_state("light.living_room") is None

    def test_returns_state_payload_and_sends_bearer(self, monkeypatch):
        monkeypatch.setattr(hass, "settings", _configured_settings())
        payload = {
            "entity_id": "light.living_room",
            "state": "on",
            "attributes": {"friendly_name": "Living Room Light"},
            "last_updated": "2026-11-13T00:00:00",
        }
        captured: dict[str, Any] = {}

        def fake_get(url, headers=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            return FakeHassResponse(payload)

        monkeypatch.setattr("httpx.get", fake_get)
        assert hass.get_entity_state("light.living_room") == payload
        assert captured["url"] == "http://hass.local/api/states/light.living_room"
        assert captured["headers"]["Authorization"] == "Bearer hass-test-token"

    def test_http_error_returns_none(self, monkeypatch):
        monkeypatch.setattr(hass, "settings", _configured_settings())

        def fake_get(url, headers=None, timeout=None):
            return FakeHassResponse({}, status_code=404)

        monkeypatch.setattr("httpx.get", fake_get)
        assert hass.get_entity_state("light.does_not_exist") is None


class TestCallService:
    def test_not_configured_returns_none(self, monkeypatch):
        monkeypatch.setattr(hass, "settings", Settings())
        assert hass.call_service("light", "turn_on", "light.living_room") is None

    def test_posts_correct_url_body_and_headers(self, monkeypatch):
        monkeypatch.setattr(hass, "settings", _configured_settings())
        captured: dict[str, Any] = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeHassResponse([{"entity_id": "light.living_room", "state": "on"}])

        monkeypatch.setattr("httpx.post", fake_post)
        result = hass.call_service("light", "turn_on", "light.living_room")
        assert result == [{"entity_id": "light.living_room", "state": "on"}]
        assert captured["url"] == "http://hass.local/api/services/light/turn_on"
        assert captured["json"] == {"entity_id": "light.living_room"}
        assert captured["headers"]["Authorization"] == "Bearer hass-test-token"
        assert captured["headers"]["Content-Type"] == "application/json"


class TestHomeDevicesEndpoint:
    def test_returns_tracked_entities_with_states(
        self, client: TestClient, auth_headers, monkeypatch
    ):
        monkeypatch.setattr(hass, "settings", _configured_settings())

        def fake_get(url, headers=None, timeout=None):
            if url.endswith("light.living_room"):
                return FakeHassResponse(
                    {"state": "on", "attributes": {"friendly_name": "Living Room Light"}, "last_updated": "2026-11-13T00:00:00"}
                )
            return FakeHassResponse(
                {"state": "off", "attributes": {"friendly_name": "Generator"}, "last_updated": "2026-11-13T00:00:00"}
            )

        monkeypatch.setattr("httpx.get", fake_get)
        resp = client.get("/api/v1/home/devices", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["configured"] is True
        by_id = {d["entity_id"]: d for d in data["devices"]}
        assert by_id["light.living_room"]["state"] == "on"
        assert by_id["light.living_room"]["reachable"] is True
        assert by_id["switch.generator"]["state"] == "off"
        assert by_id["switch.generator"]["friendly_name"] == "Generator"

    def test_not_configured_returns_unreachable_devices(
        self, client: TestClient, auth_headers, monkeypatch
    ):
        monkeypatch.setattr(hass, "settings", Settings())
        resp = client.get("/api/v1/home/devices", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["configured"] is False
        for device in data["devices"]:
            assert device["state"] is None
            assert device["reachable"] is False

    def test_unauthenticated(self, client: TestClient):
        assert client.get("/api/v1/home/devices").status_code == 401
