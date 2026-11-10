"""Supplier endpoints for inventory management."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_owner
from app.models.models import Supplier, User
from app.schemas.schemas import SupplierCreate, SupplierOut

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierOut])
def list_suppliers(
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """List all suppliers for the current user."""
    return (
        db.query(Supplier)
        .filter(Supplier.user_id == current_user.id)
        .order_by(Supplier.created_at.desc())
        .all()
    )


@router.post("", response_model=SupplierOut, status_code=201)
def create_supplier(
    body: SupplierCreate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Create a new supplier."""
    supplier = Supplier(
        user_id=current_user.id,
        name=body.name,
        email=body.email,
        phone=body.phone,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier