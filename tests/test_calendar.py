"""Tests for the calendar API and the create_calendar_event AI tool."""
from fastapi.testclient import TestClient

from app.api.chat import create_calendar_event_tool
from app.models.models import CalendarEvent, User


def _event_payload(**overrides):
    payload = {
        "title": "Team sync",
        "description": "Weekly standup",
        "start_time": "2026-11-10T14:00:00",
        "end_time": "2026-11-10T15:00:00",
        "event_type": "meeting",
    }
    payload.update(overrides)
    return payload


class TestCalendarApi:
    def test_create_and_list_event(self, client: TestClient, auth_headers):
        resp = client.post("/api/v1/calendar/events", json=_event_payload(), headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Team sync"
        assert data["event_type"] == "meeting"
        assert data["id"] is not None

        list_resp = client.get("/api/v1/calendar/events", headers=auth_headers)
        assert list_resp.status_code == 200
        events = list_resp.json()
        assert len(events) == 1
        assert events[0]["id"] == data["id"]

    def test_create_event_end_before_start(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/calendar/events",
            json=_event_payload(
                start_time="2026-11-10T15:00:00",
                end_time="2026-11-10T14:00:00",
            ),
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_list_events_filtered_by_window(self, client: TestClient, auth_headers):
        client.post(
            "/api/v1/calendar/events",
            json=_event_payload(
                start_time="2026-11-01T09:00:00",
                end_time="2026-11-01T10:00:00",
            ),
            headers=auth_headers,
        )
        client.post("/api/v1/calendar/events", json=_event_payload(), headers=auth_headers)

        resp = client.get(
            "/api/v1/calendar/events",
            params={"start": "2026-11-10T00:00:00", "end": "2026-11-11T00:00:00"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_delete_event(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/calendar/events", json=_event_payload(), headers=auth_headers)
        event_id = create.json()["id"]

        resp = client.delete(f"/api/v1/calendar/events/{event_id}", headers=auth_headers)
        assert resp.status_code == 204

        list_resp = client.get("/api/v1/calendar/events", headers=auth_headers)
        assert list_resp.json() == []

    def test_delete_event_not_found(self, client: TestClient, auth_headers):
        resp = client.delete(
            "/api/v1/calendar/events/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_calendar_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/calendar/events")
        assert resp.status_code == 401


class TestCalendarTool:
    def _make_user(self, db_session) -> User:
        user = User(email="calendar-tool@example.com", hashed_password="x", role="owner")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_tool_requires_confirmation(self, db_session):
        user = self._make_user(db_session)
        result = create_calendar_event_tool(
            db_session,
            user,
            {
                "title": "Dentist",
                "start_time": "2026-11-10T14:00:00",
                "end_time": "2026-11-10T15:00:00",
                "confirm": False,
            },
        )
        assert result["status"] == "confirmation_required"
        assert db_session.query(CalendarEvent).count() == 0

    def test_tool_creates_event(self, db_session):
        user = self._make_user(db_session)
        result = create_calendar_event_tool(
            db_session,
            user,
            {
                "title": "Schedule a meeting",
                "start_time": "2026-11-10T14:00:00",
                "end_time": "2026-11-10T15:00:00",
                "event_type": "meeting",
                "confirm": True,
            },
        )
        assert result["status"] == "created"
        assert db_session.query(CalendarEvent).count() == 1
        event = db_session.query(CalendarEvent).first()
        assert event.user_id == user.id
        assert event.title == "Schedule a meeting"

    def test_tool_rejects_invalid_time_range(self, db_session):
        user = self._make_user(db_session)
        result = create_calendar_event_tool(
            db_session,
            user,
            {
                "title": "Bad range",
                "start_time": "2026-11-10T15:00:00",
                "end_time": "2026-11-10T14:00:00",
                "confirm": True,
            },
        )
        assert result["status"] == "error"
        assert db_session.query(CalendarEvent).count() == 0
