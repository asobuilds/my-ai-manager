from uuid import UUID

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, UserConnection, Draft, JobApplication, FileCatalog
from app.schemas.schemas import (
    ConnectionCreate, ConnectionOut,
    DraftCreate, DraftOut, DraftUpdate,
    JobApplicationCreate, JobApplicationOut, JobApplicationUpdate,
    FileCatalogCreate, FileCatalogOut,
)

router = APIRouter(prefix="/me", tags=["user"])


# ── Connections ──────────────────────────────────────────────

@router.get("/connections", response_model=list[ConnectionOut])
def list_connections(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(UserConnection).filter(UserConnection.user_id == current_user.id).all()


@router.post("/connections", response_model=ConnectionOut, status_code=201)
def create_connection(body: ConnectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserConnection).filter(
        UserConnection.user_id == current_user.id,
        UserConnection.provider == body.provider,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Connection for {body.provider} already exists")
    conn = UserConnection(
        user_id=current_user.id,
        provider=body.provider,
        access_token=body.access_token,
        refresh_token=body.refresh_token,
        token_expires_at=body.token_expires_at,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


@router.delete("/connections/{connection_id}", status_code=204)
def delete_connection(
    connection_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conn = db.query(UserConnection).filter(
        UserConnection.id == connection_id,
        UserConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    db.delete(conn)
    db.commit()


# ── Drafts ───────────────────────────────────────────────────

@router.get("/drafts", response_model=list[DraftOut])
def list_drafts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Draft).filter(Draft.user_id == current_user.id).order_by(Draft.created_at.desc()).all()


@router.post("/drafts", response_model=DraftOut, status_code=201)
def create_draft(body: DraftCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    draft = Draft(user_id=current_user.id, **body.model_dump())
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.put("/drafts/{draft_id}", response_model=DraftOut)
def update_draft(
    draft_id: UUID,
    body: DraftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    draft = db.query(Draft).filter(Draft.id == draft_id, Draft.user_id == current_user.id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(draft, k, v)
    db.commit()
    db.refresh(draft)
    return draft


@router.delete("/drafts/{draft_id}", status_code=204)
def delete_draft(draft_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    draft = db.query(Draft).filter(Draft.id == draft_id, Draft.user_id == current_user.id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    db.delete(draft)
    db.commit()


# ── Job Applications ─────────────────────────────────────────

@router.get("/jobs", response_model=list[JobApplicationOut])
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(JobApplication).filter(JobApplication.user_id == current_user.id).order_by(JobApplication.created_at.desc()).all()


@router.post("/jobs", response_model=JobApplicationOut, status_code=201)
def create_job(body: JobApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = JobApplication(user_id=current_user.id, **body.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.put("/jobs/{job_id}", response_model=JobApplicationOut)
def update_job(
    job_id: UUID,
    body: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = db.query(JobApplication).filter(JobApplication.id == job_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Job application not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(app, k, v)
    db.commit()
    db.refresh(app)
    return app


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == job_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Job application not found")
    db.delete(app)
    db.commit()


# ── File Catalog ─────────────────────────────────────────────

@router.get("/files", response_model=list[FileCatalogOut])
def list_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(FileCatalog).filter(FileCatalog.user_id == current_user.id).order_by(FileCatalog.created_at.desc()).all()


@router.post("/files", response_model=FileCatalogOut, status_code=201)
def create_file(body: FileCatalogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = body.model_dump()
    tags = payload.pop("tags", None)
    catalog = FileCatalog(user_id=current_user.id, **payload)
    catalog.tags = tags
    db.add(catalog)
    db.commit()
    db.refresh(catalog)
    return catalog


@router.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    f = db.query(FileCatalog).filter(FileCatalog.id == file_id, FileCatalog.user_id == current_user.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(f)
    db.commit()
