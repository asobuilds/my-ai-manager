"""Google OAuth2 connection endpoints."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.integrations.google_auth import (
    exchange_authorization_code,
    generate_authorization_url,
)
from app.models.models import User, UserConnection

# ruff: noqa: B008

router = APIRouter(prefix="/connections", tags=["connections"])
settings = get_settings()


@router.get("/google/login")
def google_login(
    current_user: User = Depends(get_current_user),
):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")

    state = current_user.id.hex
    authorization_url = generate_authorization_url(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state,
    )
    return {"authorization_url": authorization_url}


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")

    try:
        user_id = UUID(hex=state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        access_token, refresh_token, token_expires_at = exchange_authorization_code(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
            code=code,
        )
        if token_expires_at and isinstance(token_expires_at, (int, float)):
            token_expires_at = datetime.fromtimestamp(token_expires_at, tz=UTC)
    except OSError as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange code: {e}")

    existing = db.query(UserConnection).filter(
        UserConnection.user_id == user_id,
        UserConnection.provider == "google",
    ).first()

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.token_expires_at = token_expires_at
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        connection = existing
    else:
        connection = UserConnection(
            user_id=user_id,
            provider="google",
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)

    return JSONResponse(content={
        "connection_id": str(connection.id),
        "provider": connection.provider,
        "is_active": connection.is_active,
    })
