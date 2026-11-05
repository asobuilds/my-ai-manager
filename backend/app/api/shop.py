"""Shop / Inventory management endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Product, StockMovement, User
from app.schemas.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    StockMovementCreate,
    StockMovementResponse,
)

router = APIRouter(prefix="/shop", tags=["shop"])


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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a stock movement and update the product quantity."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if body.movement_type == "out" and product.stock_quantity < body.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {product.stock_quantity}, requested: {body.quantity}",
        )

    if body.movement_type == "in":
        product.stock_quantity += body.quantity
    else:
        product.stock_quantity -= body.quantity

    movement = StockMovement(
        product_id=product_id,
        movement_type=body.movement_type,
        quantity=body.quantity,
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
