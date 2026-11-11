"""Home management endpoints for assets and maintenance tasks."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import HomeAsset, MaintenanceTask, User
from app.schemas.schemas import (
    HomeAssetCreate,
    HomeAssetOut,
    MaintenanceTaskCreate,
    MaintenanceTaskOut,
)

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/assets", response_model=list[HomeAssetOut])
def list_assets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's registered home assets."""
    return (
        db.query(HomeAsset)
        .filter(HomeAsset.user_id == current_user.id)
        .order_by(HomeAsset.name.asc())
        .all()
    )


@router.post("/assets", response_model=HomeAssetOut, status_code=201)
def create_asset(
    body: HomeAssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register a new home asset for the current user."""
    asset = HomeAsset(user_id=current_user.id, **body.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/maintenance", response_model=list[MaintenanceTaskOut])
def list_maintenance_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's maintenance tasks ordered by due date."""
    return (
        db.query(MaintenanceTask)
        .filter(MaintenanceTask.user_id == current_user.id)
        .order_by(MaintenanceTask.due_date.asc())
        .all()
    )


@router.post("/maintenance", response_model=MaintenanceTaskOut, status_code=201)
def create_maintenance_task(
    body: MaintenanceTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a maintenance task for the current user."""
    if body.asset_id is not None:
        asset = (
            db.query(HomeAsset)
            .filter(
                HomeAsset.id == body.asset_id,
                HomeAsset.user_id == current_user.id,
            )
            .first()
        )
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

    task = MaintenanceTask(user_id=current_user.id, **body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/maintenance/{task_id}", response_model=MaintenanceTaskOut)
def complete_maintenance_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark one of the current user's maintenance tasks as completed."""
    task = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.id == task_id,
            MaintenanceTask.user_id == current_user.id,
        )
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Maintenance task not found")

    task.is_completed = True
    db.commit()
    db.refresh(task)
    return task
