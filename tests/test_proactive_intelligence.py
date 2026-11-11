"""Tests for proactive intelligence: analytics and daily reports."""
from datetime import datetime, timedelta

from fastapi.testclient import TestClient


class TestShopAnalytics:
    def test_analytics_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/shop/analytics", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_revenue"] == 0.0
        assert data["top_products"] == []
        assert data["avg_daily_sales"] == 0.0

    def test_analytics_with_sales(self, client: TestClient, db_session):
        from app.models.models import Product, StockMovement, User
        from app.core.security import hash_password

        user = User(
            email="analytics_test@test.com",
            hashed_password=hash_password("testpass123"),
            role="owner",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        product = Product(
            user_id=user.id,
            sku="ANALYTICS-TEST",
            name="Test Widget",
            price=1000,
            stock_quantity=50,
            reorder_level=10,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        now = datetime.utcnow()
        # All sales on the same day so avg_daily_sales reflects total units
        for i in range(3):
            movement = StockMovement(
                product_id=product.id,
                movement_type="out",
                quantity=5,
                reason="sale",
                created_at=now,
            )
            db_session.add(movement)
        db_session.commit()

        resp_login = client.post(
            "/api/v1/auth/login",
            json={"email": "analytics_test@test.com", "password": "testpass123"},
        )
        token = resp_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/v1/shop/analytics", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_revenue"] == 150.0
        assert len(data["top_products"]) == 1
        assert data["top_products"][0]["name"] == "Test Widget"
        assert data["top_products"][0]["units_sold"] == 15

    def test_daily_report_endpoint_no_report(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/shop/daily-report", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() is None


class TestScheduler:
    def test_scheduler_starts(self):
        from app.services.scheduler import start_scheduler, get_scheduler, shutdown_scheduler

        start_scheduler()
        sched = get_scheduler()
        assert sched is not None
        assert sched.running
        jobs = sched.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].name == "Daily Report Generation"
        shutdown_scheduler()
