"""Social Media Management endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_owner
from app.models.models import SocialPost, User
from app.schemas.schemas import (
    SocialGenerateRequest,
    SocialPostCreate,
    SocialPostOut,
    SocialPostUpdate,
)
from app.services.social_generator import generate_promo_post

router = APIRouter(prefix="/social", tags=["social"])


@router.get("/posts", response_model=list[SocialPostOut])
def list_social_posts(
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """List all social media posts for the current user."""
    return (
        db.query(SocialPost)
        .filter(SocialPost.user_id == current_user.id)
        .order_by(SocialPost.created_at.desc())
        .all()
    )


@router.post("/posts", response_model=SocialPostOut, status_code=201)
def create_social_post(
    body: SocialPostCreate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Create a new social media post (draft, scheduled, or published)."""
    post = SocialPost(user_id=current_user.id, **body.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch("/posts/{post_id}", response_model=SocialPostOut)
def update_social_post(
    post_id: UUID,
    body: SocialPostUpdate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Update a social media post's status, content, platform, or scheduled time."""
    post = (
        db.query(SocialPost)
        .filter(SocialPost.id == post_id, SocialPost.user_id == current_user.id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


@router.post("/generate", response_model=dict)
async def generate_post_content(
    body: SocialGenerateRequest,
    current_user: User = Depends(get_current_owner),
):
    """Generate a promotional post caption using AI."""
    caption = await generate_promo_post(body.product_name, body.platform)
    return {"content": caption, "platform": body.platform, "product_name": body.product_name}
