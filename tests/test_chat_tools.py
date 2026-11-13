"""Tests for the chat AI tool handlers (shop, health, home)."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.api.chat import (
    check_low_stock_tool,
    get_home_maintenance_tool,
    get_health_vitals_tool,
    get_shop_analytics_tool,
)
from app.models.models import (
    HealthProfile,
    HealthVitals,
    MaintenanceTask,
    Product,
    StockMovement,
    User,
)


class MockResponse:
    def __init__(self, json_data: dict | None = None):
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        pass


def _make_user(db, email: str) -> User:
    user = User(email=email, hashed_password="placeholder", role="owner")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestCheckLowStockTool:
    def test_returns_only_low_and_at_level(self, db_session):
        user = _make_user(db_session, "lowstock@example.com")
        db_session.add(Product(user_id=user.id, sku="LOW-1", name="Low Item", price=100, stock_quantity=0, reorder_level=5))
        db_session.add(Product(user_id=user.id, sku="AT-1", name="At Level", price=100, stock_quantity=5, reorder_level=5))
        db_session.add(Product(user_id=user.id, sku="OK-1", name="Healthy", price=100, stock_quantity=50, reorder_level=5))
        db_session.commit()

        result = check_low_stock_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["count"] == 2
        assert {item["name"] for item in result["low_stock"]} == {"Low Item", "At Level"}

    def test_scoped_to_user(self, db_session):
        user_a = _make_user(db_session, "user-a@example.com")
        user_b = _make_user(db_session, "user-b@example.com")
        db_session.add(Product(user_id=user_a.id, sku="A-LOW", name="A Low", price=100, stock_quantity=0, reorder_level=5))
        db_session.add(Product(user_id=user_b.id, sku="B-LOW", name="B Low", price=100, stock_quantity=0, reorder_level=5))
        db_session.commit()

        result = check_low_stock_tool(db_session, user_a, {})
        assert [item["sku"] for item in result["low_stock"]] == ["A-LOW"]

    def test_empty(self, db_session):
        user = _make_user(db_session, "empty@example.com")
        result = check_low_stock_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["count"] == 0
        assert result["low_stock"] == []


class TestGetShopAnalyticsTool:
    def test_computes_revenue_and_top_products(self, db_session):
        user = _make_user(db_session, "analytics@example.com")
        p = Product(user_id=user.id, sku="AN-1", name="Widget", price=200)
        db_session.add(p)
        db_session.commit()
        db_session.refresh(p)
        for _ in range(3):
            db_session.add(
                StockMovement(product_id=p.id, movement_type="out", quantity=2, quantity_in_base_units=2, created_at=datetime.now())
            )
        db_session.commit()

        result = get_shop_analytics_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["total_revenue"] == 12.0  # 6 units * $2.00
        assert result["top_products"][0] == {"name": "Widget", "units_sold": 6}
        assert result["period_start"] and result["period_end"]

    def test_no_movements(self, db_session):
        user = _make_user(db_session, "noanalytics@example.com")
        result = get_shop_analytics_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["total_revenue"] == 0.0
        assert result["top_products"] == []
        assert result["avg_daily_sales"] == 0.0


class TestGetHealthVitalsTool:
    def test_returns_latest_vitals_and_blood_type(self, db_session):
        user = _make_user(db_session, "health@example.com")
        db_session.add(HealthProfile(user_id=user.id, blood_type="A+", genotype="AA"))
        db_session.add(
            HealthVitals(
                user_id=user.id,
                systolic=120,
                diastolic=80,
                heart_rate=70,
                weight=70.0,
                steps=5000,
                calories=2000,
                recorded_at=datetime.now(),
            )
        )
        db_session.commit()

        result = get_health_vitals_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["blood_type"] == "A+"
        assert result["genotype"] == "AA"
        assert result["latest_vitals"]["systolic"] == 120
        assert result["latest_vitals"]["heart_rate"] == 70

    def test_no_vitals(self, db_session):
        user = _make_user(db_session, "health-empty@example.com")
        result = get_health_vitals_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["latest_vitals"] is None
        assert result["blood_type"] is None


class TestGetHomeMaintenanceTool:
    def test_returns_only_pending_tasks(self, db_session):
        user = _make_user(db_session, "home@example.com")
        db_session.add(MaintenanceTask(user_id=user.id, title="Pending task", due_date=datetime(2026, 12, 1, 9, 0), is_completed=False))
        db_session.add(MaintenanceTask(user_id=user.id, title="Done task", due_date=datetime(2026, 11, 1, 9, 0), is_completed=True))
        db_session.commit()

        result = get_home_maintenance_tool(db_session, user, {})
        assert result["status"] == "ok"
        assert result["count"] == 1
        assert result["pending_tasks"][0]["title"] == "Pending task"

    def test_scoped_to_user(self, db_session):
        user_a = _make_user(db_session, "home-a@example.com")
        user_b = _make_user(db_session, "home-b@example.com")
        db_session.add(MaintenanceTask(user_id=user_a.id, title="A task", due_date=datetime(2026, 12, 1, 9, 0), is_completed=False))
        db_session.add(MaintenanceTask(user_id=user_b.id, title="B task", due_date=datetime(2026, 12, 1, 9, 0), is_completed=False))
        db_session.commit()

        result = get_home_maintenance_tool(db_session, user_a, {})
        assert [t["title"] for t in result["pending_tasks"]] == ["A task"]


class TestMultiRoundToolLoop:
    def test_sequential_tool_rounds(self, client, auth_headers, db_session):
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        db_session.add(Product(user_id=user.id, sku="MR-LOW", name="Mr Low", price=50, stock_quantity=0, reorder_level=5))
        db_session.add(HealthProfile(user_id=user.id, blood_type="B", genotype="AS"))
        db_session.add(
            HealthVitals(
                user_id=user.id,
                systolic=118,
                diastolic=76,
                heart_rate=72,
                weight=71.0,
                steps=4000,
                calories=1800,
                recorded_at=datetime.now(),
            )
        )
        db_session.commit()

        responses = [
            # Round 1: model asks for low stock.
            {"choices": [{"message": {"content": "", "tool_calls": [
                {"id": "c1", "type": "function", "function": {"name": "check_low_stock", "arguments": "{}"}}
            ]}}]},
            # Round 2: model follows up with health vitals.
            {"choices": [{"message": {"content": "", "tool_calls": [
                {"id": "c2", "type": "function", "function": {"name": "get_health_vitals", "arguments": "{}"}}
            ]}}]},
            # Round 3: final answer, no more tools.
            {"choices": [{"message": {"content": "Final: 1 low-stock item, BP 118/76."}}]},
        ]

        with patch("app.api.chat.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=[MockResponse(r) for r in responses])
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.post(
                "/api/v1/chat/",
                json={"message": "Summarize my stock and health"},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["response"] == "Final: 1 low-stock item, BP 118/76."
        # Two tool rounds executed → three Agnes calls total.
        assert mock_client.post.call_count == 3
