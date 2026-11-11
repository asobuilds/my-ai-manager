"""Proactive daily analytics via APScheduler + Pandas."""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models.models import DailyReport, Product, StockMovement, User

logger = logging.getLogger(__name__)


def _build_report(user: User, db: Session) -> tuple[str, int]:
    """Return (report_text, low_stock_count) for one user."""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)

    movements_today = (
        db.query(StockMovement)
        .join(Product)
        .filter(
            Product.user_id == user.id,
            StockMovement.movement_type == "out",
            StockMovement.created_at >= start_of_day,
            StockMovement.created_at < end_of_day,
        )
        .all()
    )

    df = pd.DataFrame([
        {
            "product": m.product.name if m.product else "Unknown",
            "sku": m.product.sku if m.product else "",
            "quantity": m.quantity,
            "price_cents": m.product.price if m.product else 0,
            "created_at": m.created_at,
        }
        for m in movements_today
    ])

    total_units_sold = int(df["quantity"].sum()) if not df.empty else 0
    total_revenue = round((df["quantity"] * df["price_cents"]).sum() / 100, 2) if not df.empty else 0.0

    product_sales: dict[str, int] = {}
    if not df.empty:
        for _, row in df.iterrows():
            product_sales[row["product"]] += int(row["quantity"])
    top_items = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:3]

    low_stock = (
        db.query(Product)
        .filter(
            Product.user_id == user.id,
            Product.stock_quantity <= Product.reorder_level,
        )
        .all()
    )
    low_stock_count = len(low_stock)
    low_stock_names = ", ".join(p.name for p in low_stock[:5]) or "none"

    lines = [f"Daily Sales Report for {today.isoformat()}", ""]
    lines.append(f"Total items sold today: {total_units_sold}")
    lines.append(f"Total revenue today: ${total_revenue:.2f}")

    if top_items:
        lines.append("Top-selling products:")
        for name, qty in top_items:
            lines.append(f"  - {name}: {qty} units")
    else:
        lines.append("No sales recorded today.")

    lines.append("")
    lines.append(f"Low-stock alerts: {low_stock_count} item(s)")
    if low_stock:
        for p in low_stock:
            lines.append(f"  - {p.name} (SKU: {p.sku}): {p.stock_quantity}/{p.reorder_level}")
    else:
        lines.append("  All stock levels healthy.")

    report_text = "\n".join(lines)
    return report_text, low_stock_count


def generate_daily_report(db: Session, user: User) -> DailyReport:
    """Generate a daily report for a single user and persist it."""
    report_text, _ = _build_report(user, db)
    report = DailyReport(user_id=user.id, report_text=report_text)
    db.add(report)
    db.commit()
    db.refresh(report)
    logger.info("Daily report generated for user %s", user.email)
    return report


def run_all_daily_reports(db: Session) -> list[DailyReport]:
    """Generate reports for every active user."""
    users = db.query(User).filter(User.is_active == True).all()  # noqa: E712
    reports: list[DailyReport] = []
    for user in users:
        try:
            reports.append(generate_daily_report(db, user))
        except Exception as exc:
            logger.error("Failed to generate report for user %s: %s", user.email, exc)
    return reports
