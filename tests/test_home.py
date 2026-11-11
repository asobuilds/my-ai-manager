"""Tests for the home management API endpoints."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.models.models import HomeAsset, MaintenanceTask, User


class MockResponse:
    def __init__(self, status_code: int = 200, json_data: dict | None = None):
        self._status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self._status_code >= 400:
            raise Exception(f"HTTP {self._status_code}")


def _asset_payload(**overrides):
    payload = {
        "name": "Washing Machine",
        "category": "Appliance",
        "serial_number": "WM-12345",
        "purchase_date": "2025-01-15T00:00:00",
        "warranty_expiry": "2027-01-15T00:00:00",
    }
    payload.update(overrides)
    return payload


def _task_payload(**overrides):
    payload = {
        "title": "Replace water filter",
        "description": "Change the filter every six months",
        "due_date": "2026-12-01T09:00:00",
        "is_recurring": True,
        "recurrence_days": 180,
    }
    payload.update(overrides)
    return payload


class TestHomeAssets:
    def test_list_assets_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/home/assets", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_asset(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/home/assets",
            json=_asset_payload(),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Washing Machine"
        assert data["category"] == "Appliance"
        assert data["serial_number"] == "WM-12345"
        assert data["purchase_date"] is not None
        assert data["warranty_expiry"] is not None
        assert data["id"] is not None
        assert data["user_id"] is not None

    def test_create_asset_minimal(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/home/assets",
            json={"name": "Generator", "category": "Equipment"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Generator"
        assert data["serial_number"] is None

    def test_list_assets(self, client: TestClient, auth_headers):
        client.post("/api/v1/home/assets", json=_asset_payload(name="Fridge"), headers=auth_headers)
        client.post("/api/v1/home/assets", json=_asset_payload(name="AC Unit"), headers=auth_headers)

        resp = client.get("/api/v1/home/assets", headers=auth_headers)
        assert resp.status_code == 200
        names = [asset["name"] for asset in resp.json()]
        assert names == ["AC Unit", "Fridge"]

    def test_assets_unauthenticated(self, client: TestClient):
        assert client.get("/api/v1/home/assets").status_code == 401
        assert client.post("/api/v1/home/assets", json=_asset_payload()).status_code == 401


class TestMaintenanceTasks:
    def test_create_task(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/home/maintenance",
            json=_task_payload(),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Replace water filter"
        assert data["is_recurring"] is True
        assert data["recurrence_days"] == 180
        assert data["is_completed"] is False
        assert data["asset_id"] is None

    def test_create_task_with_asset(self, client: TestClient, auth_headers):
        asset = client.post(
            "/api/v1/home/assets",
            json=_asset_payload(),
            headers=auth_headers,
        ).json()

        resp = client.post(
            "/api/v1/home/maintenance",
            json=_task_payload(asset_id=asset["id"]),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["asset_id"] == asset["id"]

    def test_create_task_with_unknown_asset(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/home/maintenance",
            json=_task_payload(asset_id="00000000-0000-0000-0000-000000000000"),
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_list_tasks_ordered_by_due_date(self, client: TestClient, auth_headers):
        client.post(
            "/api/v1/home/maintenance",
            json=_task_payload(title="Later task", due_date="2026-12-15T09:00:00"),
            headers=auth_headers,
        )
        client.post(
            "/api/v1/home/maintenance",
            json=_task_payload(title="Sooner task", due_date="2026-11-20T09:00:00"),
            headers=auth_headers,
        )

        resp = client.get("/api/v1/home/maintenance", headers=auth_headers)
        assert resp.status_code == 200
        titles = [task["title"] for task in resp.json()]
        assert titles == ["Sooner task", "Later task"]

    def test_complete_task(self, client: TestClient, auth_headers):
        task = client.post(
            "/api/v1/home/maintenance",
            json=_task_payload(),
            headers=auth_headers,
        ).json()
        assert task["is_completed"] is False

        resp = client.patch(
            f"/api/v1/home/maintenance/{task['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_completed"] is True

        list_resp = client.get("/api/v1/home/maintenance", headers=auth_headers)
        assert list_resp.json()[0]["is_completed"] is True

    def test_complete_task_not_found(self, client: TestClient, auth_headers):
        resp = client.patch(
            "/api/v1/home/maintenance/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_maintenance_unauthenticated(self, client: TestClient):
        assert client.get("/api/v1/home/maintenance").status_code == 401
        assert client.post("/api/v1/home/maintenance", json=_task_payload()).status_code == 401
        assert (
            client.patch(
                "/api/v1/home/maintenance/00000000-0000-0000-0000-000000000000"
            ).status_code
            == 401
        )


class TestHomeChatContext:
    def test_system_prompt_includes_home_context(
        self, client: TestClient, auth_headers, db_session
    ):
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        asset = HomeAsset(user_id=user.id, name="Dishwasher", category="Appliance")
        db_session.add(asset)
        db_session.commit()
        db_session.refresh(asset)
        db_session.add(
            MaintenanceTask(
                user_id=user.id,
                asset_id=asset.id,
                title="Clean dishwasher filter",
                due_date=datetime(2026, 12, 1, 9, 0),
                is_completed=False,
            )
        )
        db_session.add(
            MaintenanceTask(
                user_id=user.id,
                title="Old completed task",
                due_date=datetime(2026, 10, 1, 9, 0),
                is_completed=True,
            )
        )
        db_session.commit()

        mock_body = {"choices": [{"message": {"content": "Here is your home status."}}]}
        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_resp = MockResponse(json_data=mock_body)
            mock_client.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post(
                "/api/v1/chat",
                json={"message": "What maintenance is due?"},
                headers=auth_headers,
            )
            assert resp.status_code == 200

            payload = mock_client.post.call_args.kwargs["json"]
            system_prompt = payload["messages"][0]["content"]
            assert "User Home Context: You have 1 registered assets." in system_prompt
            assert "Clean dishwasher filter" in system_prompt
            assert "Old completed task" not in system_prompt
            assert "use this context to answer" in system_prompt
