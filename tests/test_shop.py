"""Tests for the shop/inventory API endpoints."""
from uuid import uuid4

from fastapi.testclient import TestClient


class TestShopProducts:
    def test_list_products_empty(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/shop/products", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_product(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/v1/shop/products",
            json={
                "sku": "TEST-001",
                "name": "Widget",
                "category": "Supplies",
                "price": 999,
                "stock_quantity": 50,
                "reorder_level": 10,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["sku"] == "TEST-001"
        assert data["name"] == "Widget"
        assert data["price"] == 999
        assert data["stock_quantity"] == 50

    def test_create_product_duplicate_sku(self, client: TestClient, auth_headers):
        client.post(
            "/api/v1/shop/products",
            json={
                "sku": "DUPE-001",
                "name": "Widget",
                "price": 500,
            },
            headers=auth_headers,
        )
        resp = client.post(
            "/api/v1/shop/products",
            json={
                "sku": "DUPE-001",
                "name": "Another Widget",
                "price": 600,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"]

    def test_update_product(self, client: TestClient, auth_headers):
        create = client.post(
            "/api/v1/shop/products",
            json={"sku": "UPD-001", "name": "Old Name", "price": 1000},
            headers=auth_headers,
        )
        product_id = create.json()["id"]
        resp = client.patch(
            f"/api/v1/shop/products/{product_id}",
            json={"name": "New Name", "price": 2000},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["price"] == 2000

    def test_update_product_not_found(self, client: TestClient, auth_headers):
        fake_id = str(uuid4())
        resp = client.patch(
            f"/api/v1/shop/products/{fake_id}",
            json={"name": "Nope"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestStockMovements:
    def test_add_stock_in(self, client: TestClient, auth_headers):
        create = client.post(
            "/api/v1/shop/products",
            json={"sku": "MOV-001", "name": "Gadget", "price": 500, "stock_quantity": 0},
            headers=auth_headers,
        )
        product_id = create.json()["id"]

        resp = client.post(
            f"/api/v1/shop/products/{product_id}/stock",
            json={"movement_type": "in", "quantity": 100, "reason": "restock"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["movement_type"] == "in"
        assert data["quantity"] == 100

        # Verify product stock was updated
        product_resp = client.get("/api/v1/shop/products", headers=auth_headers)
        product = next(p for p in product_resp.json() if p["id"] == product_id)
        assert product["stock_quantity"] == 100

    def test_add_stock_out(self, client: TestClient, auth_headers):
        create = client.post(
            "/api/v1/shop/products",
            json={"sku": "OUT-001", "name": "Thingamajig", "price": 250, "stock_quantity": 10},
            headers=auth_headers,
        )
        product_id = create.json()["id"]

        resp = client.post(
            f"/api/v1/shop/products/{product_id}/stock",
            json={"movement_type": "out", "quantity": 3, "reason": "sale"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

        product_resp = client.get("/api/v1/shop/products", headers=auth_headers)
        product = next(p for p in product_resp.json() if p["id"] == product_id)
        assert product["stock_quantity"] == 7

    def test_stock_out_insufficient_quantity(self, client: TestClient, auth_headers):
        create = client.post(
            "/api/v1/shop/products",
            json={"sku": "INS-001", "name": "Thing", "price": 100, "stock_quantity": 2},
            headers=auth_headers,
        )
        product_id = create.json()["id"]

        resp = client.post(
            f"/api/v1/shop/products/{product_id}/stock",
            json={"movement_type": "out", "quantity": 5, "reason": "sale"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "Insufficient stock" in resp.json()["detail"]
        # Stock should not have changed
        product_resp = client.get("/api/v1/shop/products", headers=auth_headers)
        product = next(p for p in product_resp.json() if p["id"] == product_id)
        assert product["stock_quantity"] == 2

    def test_stock_movement_not_found(self, client: TestClient, auth_headers):
        fake_id = str(uuid4())
        resp = client.post(
            f"/api/v1/shop/products/{fake_id}/stock",
            json={"movement_type": "in", "quantity": 10},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestLowStockAlerts:
    def test_low_stock_alerts_empty(self, client: TestClient, auth_headers):
        # Create a product well above reorder level
        client.post(
            "/api/v1/shop/products",
            json={"sku": "ALERT-001", "name": "Plenty", "price": 100, "stock_quantity": 100, "reorder_level": 5},
            headers=auth_headers,
        )
        resp = client.get("/api/v1/shop/alerts/low-stock", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_low_stock_alerts_triggers(self, client: TestClient, auth_headers):
        # Create a product at reorder level
        client.post(
            "/api/v1/shop/products",
            json={"sku": "LOW-001", "name": "Running Low", "price": 200, "stock_quantity": 5, "reorder_level": 5},
            headers=auth_headers,
        )
        resp = client.get("/api/v1/shop/alerts/low-stock", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["sku"] == "LOW-001"
        assert data[0]["stock_quantity"] == data[0]["reorder_level"]

    def test_low_stock_alerts_multiple(self, client: TestClient, auth_headers):
        # One product above reorder level (should NOT appear)
        client.post(
            "/api/v1/shop/products",
            json={"sku": "FINE-001", "name": "Well Stocked", "price": 100, "stock_quantity": 50, "reorder_level": 5},
            headers=auth_headers,
        )
        # Two products at or below reorder level (should appear)
        client.post(
            "/api/v1/shop/products",
            json={"sku": "LOW-002", "name": "Empty", "price": 50, "stock_quantity": 0, "reorder_level": 10},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/shop/products",
            json={"sku": "LOW-003", "name": "Meets Reorder", "price": 75, "stock_quantity": 3, "reorder_level": 3},
            headers=auth_headers,
        )
        resp = client.get("/api/v1/shop/alerts/low-stock", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        skus = {p["sku"] for p in data}
        assert skus == {"LOW-002", "LOW-003"}
        # Verify sorted by stock_quantity ascending
        assert data[0]["stock_quantity"] <= data[1]["stock_quantity"]
