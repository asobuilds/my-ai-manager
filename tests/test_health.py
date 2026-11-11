"""Tests for the health profile and vitals API endpoints."""
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.models.models import HealthProfile, HealthVitals, User


class MockResponse:
    def __init__(self, status_code: int = 200, json_data: dict | None = None):
        self._status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self._status_code >= 400:
            raise Exception(f"HTTP {self._status_code}")


def _vitals_payload(**overrides):
    payload = {
        "systolic": 120,
        "diastolic": 80,
        "heart_rate": 72,
        "weight": 70.5,
        "steps": 8500,
        "calories": 2100,
    }
    payload.update(overrides)
    return payload


class TestHealthProfile:
    def test_get_profile_creates_default(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/health/profile", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] is not None
        assert data["user_id"] is not None
        assert data["blood_type"] is None
        assert data["genotype"] is None
        assert data["allergies"] is None
        assert data["medical_conditions"] is None

    def test_get_profile_is_idempotent(self, client: TestClient, auth_headers):
        first = client.get("/api/v1/health/profile", headers=auth_headers)
        second = client.get("/api/v1/health/profile", headers=auth_headers)
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["id"] == second.json()["id"]

    def test_update_profile(self, client: TestClient, auth_headers):
        resp = client.put(
            "/api/v1/health/profile",
            json={
                "blood_type": "O+",
                "genotype": "AA",
                "allergies": "Peanuts",
                "medical_conditions": "Asthma",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["blood_type"] == "O+"
        assert data["genotype"] == "AA"
        assert data["allergies"] == "Peanuts"
        assert data["medical_conditions"] == "Asthma"

        get_resp = client.get("/api/v1/health/profile", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["blood_type"] == "O+"

    def test_update_profile_partial(self, client: TestClient, auth_headers):
        client.put(
            "/api/v1/health/profile",
            json={"blood_type": "A+", "genotype": "AS"},
            headers=auth_headers,
        )
        resp = client.put(
            "/api/v1/health/profile",
            json={"allergies": "Dust"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["blood_type"] == "A+"
        assert data["genotype"] == "AS"
        assert data["allergies"] == "Dust"

    def test_profile_unauthenticated(self, client: TestClient):
        assert client.get("/api/v1/health/profile").status_code == 401
        assert client.put("/api/v1/health/profile", json={}).status_code == 401


class TestHealthVitals:
    def test_create_vitals(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/health/vitals",
            json=_vitals_payload(),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["systolic"] == 120
        assert data["diastolic"] == 80
        assert data["heart_rate"] == 72
        assert data["weight"] == 70.5
        assert data["steps"] == 8500
        assert data["calories"] == 2100
        assert data["recorded_at"] is not None
        assert data["id"] is not None

    def test_create_vitals_defaults_recorded_at(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/health/vitals",
            json={"systolic": 118, "diastolic": 76, "heart_rate": 68},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["recorded_at"] is not None

    def test_list_vitals_ordered_desc(self, client: TestClient, auth_headers):
        client.post(
            "/api/v1/health/vitals",
            json=_vitals_payload(recorded_at="2026-11-09T08:00:00", systolic=115),
            headers=auth_headers,
        )
        client.post(
            "/api/v1/health/vitals",
            json=_vitals_payload(recorded_at="2026-11-10T08:00:00", systolic=125),
            headers=auth_headers,
        )

        resp = client.get("/api/v1/health/vitals", headers=auth_headers)
        assert resp.status_code == 200
        vitals = resp.json()
        assert len(vitals) == 2
        assert vitals[0]["systolic"] == 125
        assert vitals[1]["systolic"] == 115

    def test_list_vitals_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/health/vitals", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_vitals_unauthenticated(self, client: TestClient):
        assert client.post("/api/v1/health/vitals", json=_vitals_payload()).status_code == 401
        assert client.get("/api/v1/health/vitals").status_code == 401


class TestHealthChatContext:
    def test_system_prompt_includes_health_context(
        self, client: TestClient, auth_headers, db_session
    ):
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        db_session.add(
            HealthProfile(
                user_id=user.id,
                blood_type="O+",
                genotype="AA",
                allergies="Peanuts",
            )
        )
        db_session.add(
            HealthVitals(
                user_id=user.id,
                systolic=121,
                diastolic=79,
                heart_rate=70,
                weight=69.0,
                steps=9000,
                calories=2200,
            )
        )
        db_session.commit()

        mock_body = {"choices": [{"message": {"content": "Stay well!"}}]}
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(json_data=mock_body)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post(
                "/api/v1/chat",
                json={"message": "How is my health?"},
                headers=auth_headers,
            )
            assert resp.status_code == 200

            payload = mock_client.post.call_args.kwargs["json"]
            system_prompt = payload["messages"][0]["content"]
            assert "User Health Context: Blood Type: O+, Genotype: AA." in system_prompt
            assert "Latest Vitals: BP 121/79, HR 70, Steps today: 9000." in system_prompt
            assert "recommend consulting a doctor" in system_prompt
            assert "Do not diagnose" in system_prompt
