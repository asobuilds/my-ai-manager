"""Health profile and vitals endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import HealthProfile, HealthVitals, User
from app.schemas.schemas import (
    HealthProfileCreate,
    HealthProfileOut,
    HealthVitalsCreate,
    HealthVitalsOut,
)

router = APIRouter(prefix="/health", tags=["health"])


def _get_or_create_profile(db: Session, user: User) -> HealthProfile:
    profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == user.id)
        .first()
    )
    if not profile:
        profile = HealthProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/profile", response_model=HealthProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's health profile, creating a default one if missing."""
    return _get_or_create_profile(db, current_user)


@router.put("/profile", response_model=HealthProfileOut)
def update_profile(
    body: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's health profile."""
    profile = _get_or_create_profile(db, current_user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/vitals", response_model=HealthVitalsOut, status_code=201)
def create_vitals(
    body: HealthVitalsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log a new vitals record for the current user."""
    data = body.model_dump(exclude_unset=True)
    if data.get("recorded_at") is None:
        data.pop("recorded_at", None)
    vitals = HealthVitals(user_id=current_user.id, **data)
    db.add(vitals)
    db.commit()
    db.refresh(vitals)
    return vitals


@router.get("/vitals", response_model=list[HealthVitalsOut])
def list_vitals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's vitals, newest first."""
    return (
        db.query(HealthVitals)
        .filter(HealthVitals.user_id == current_user.id)
        .order_by(HealthVitals.recorded_at.desc())
        .all()
    )
