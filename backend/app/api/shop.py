"""Shop / Inventory management endpoints."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_owner, get_current_user
from app.models.models import DailyReport, Product, StockMovement, User
from app.schemas.schemas import (
    DailyReportOut,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    SalesSummary,
    StockMovementCreate,
    StockMovementResponse,
)

router = APIRouter(prefix="/shop", tags=["shop"])
settings = get_settings()

async def _call_agnes(payload: dict[str, Any]) -> dict[str, Any]:
    base_url = settings.AGNES_BASE_URL.rstrip("/")
    url = base_url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
    except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI API error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI request failed: {exc}")


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all products for the current user."""
    return (
        db.query(Product)
        .filter(Product.user_id == current_user.id)
        .order_by(Product.created_at.desc())
        .all()
    )


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    body: ProductCreate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Create a new product."""
    existing = db.query(Product).filter(Product.sku == body.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"SKU '{body.sku}' already exists")

    product = Product(
        user_id=current_user.id,
        **body.model_dump(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    body: ProductUpdate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Update a product's details."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.post("/products/{product_id}/stock", response_model=StockMovementResponse)
def add_stock_movement(
    product_id: UUID,
    body: StockMovementCreate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Record a stock movement and update the product quantity."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Determine the unit used and convert to base units
    original_unit = body.original_unit or "piece"
    if original_unit == "carton":
        quantity_in_base_units = body.quantity * product.units_per_carton
    else:
        quantity_in_base_units = body.quantity

    if body.movement_type == "out" and product.stock_quantity < quantity_in_base_units:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {product.stock_quantity} pieces, requested: {quantity_in_base_units} pieces ({body.quantity} {original_unit}s)",
        )

    if body.movement_type == "in":
        product.stock_quantity += quantity_in_base_units
    else:
        product.stock_quantity -= quantity_in_base_units

    movement = StockMovement(
        product_id=product_id,
        movement_type=body.movement_type,
        quantity=body.quantity,
        original_unit=original_unit,
        quantity_in_base_units=quantity_in_base_units,
        reason=body.reason,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/alerts/low-stock", response_model=list[ProductResponse])
def low_stock_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return products where stock_quantity <= reorder_level."""
    return (
        db.query(Product)
        .filter(
            Product.user_id == current_user.id,
            Product.stock_quantity <= Product.reorder_level,
        )
        .order_by(Product.stock_quantity.asc())
        .all()
    )


@router.post("/reorder/{product_id}", response_model=dict[str, Any])
async def reorder_product(
    product_id: UUID,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Generate an AI-powered reorder email draft for a low-stock product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    supplier = product.supplier
    if not supplier:
        raise HTTPException(status_code=400, detail="Product has no supplier assigned")

    now = datetime.now()
    system_prompt = f"""You are Aso, a dedicated personal AI assistant. Generate a professional reorder email for the supplier.

User Context:
- Name: {current_user.full_name or 'the user'}
- Role: {current_user.role}
- Location: {current_user.location or 'unknown'}

Supplier: {supplier.name}
Supplier Email: {supplier.email or 'not provided'}
Supplier Phone: {supplier.phone or 'not provided'}

Product: {product.name}
SKU: {product.sku}
Current Stock: {product.stock_quantity}
Reorder Level: {product.reorder_level}
Price: ${product.price / 100:.2f}

Generate a professional, concise email draft asking the supplier to restock {product.reorder_level} units of {product.name} (SKU: {product.sku}). The email should be polite, include all necessary details, and be ready to send."""
    
    user_prompt = "Please generate the reorder email draft now."

    messages_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    payload = {
        "model": "agnes-2.5-flash",
        "messages": messages_history,
    }

    data = await _call_agnes(payload)
    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="No response from Agnes AI")

    response_text = choices[0].get("message", {}).get("content", "")
    return {"draft": response_text, "supplier_email": supplier.email, "product_name": product.name}


# ---------- Analytics ----------

@router.get("/analytics", response_model=SalesSummary)
def get_shop_analytics(
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Return Pandas-powered sales summary for the current user this week."""
    from datetime import date, timedelta

    import pandas as pd

    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    movements = (
        db.query(StockMovement)
        .join(Product)
        .filter(
            Product.user_id == current_user.id,
            StockMovement.movement_type == "out",
            StockMovement.created_at >= start_dt,
            StockMovement.created_at <= end_dt,
        )
        .all()
    )

    df = pd.DataFrame([
        {
            "product": m.product.name if m.product else "Unknown",
            "sku": m.product.sku if m.product else "",
            "quantity": m.quantity,
            "price_cents": m.product.price if m.product else 0,
            "date": m.created_at.date() if m.created_at else None,
        }
        for m in movements
    ])

    total_revenue = round((df["quantity"] * df["price_cents"]).sum() / 100, 2) if not df.empty else 0.0

    if df.empty:
        top_list: list[dict[str, Any]] = []
        avg_daily = 0.0
    else:
        top_products = (
            df.groupby("product")["quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
            .reset_index()
        )
        top_list = [
            {"name": row["product"], "units_sold": int(row["quantity"])}
            for _, row in top_products.iterrows()
        ]

        daily_counts = df.dropna(subset=["date"]).groupby("date").size()
        avg_daily = round(float(daily_counts.mean()), 2) if len(daily_counts) > 0 else 0.0

    return SalesSummary(
        total_revenue=total_revenue,
        top_products=top_list,
        avg_daily_sales=avg_daily,
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
    )


@router.get("/daily-report", response_model=DailyReportOut | None)
def get_latest_daily_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the most recent daily report for the current user, if any."""
    report = (
        db.query(DailyReport)
        .filter(DailyReport.user_id == current_user.id)
        .order_by(DailyReport.created_at.desc())
        .first()
    )
    return report
