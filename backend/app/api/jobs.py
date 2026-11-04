"""Job application tracker endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import JobApplication, User
from app.schemas.schemas import JobApplicationCreate, JobApplicationOut, JobApplicationUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobApplicationOut])
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all job applications for the current user."""
    return (
        db.query(JobApplication)
        .filter(JobApplication.user_id == current_user.id)
        .order_by(JobApplication.created_at.desc())
        .all()
    )


@router.post("", response_model=JobApplicationOut, status_code=201)
def create_job(body: JobApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new job application."""
    app = JobApplication(user_id=current_user.id, **body.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.patch("/{job_id}", response_model=JobApplicationOut)
def update_job(
    job_id: UUID,
    body: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a job application's status or notes."""
    app = (
        db.query(JobApplication)
        .filter(JobApplication.id == job_id, JobApplication.user_id == current_user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Job application not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app
