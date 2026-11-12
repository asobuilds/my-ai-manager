"""User preferences endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_owner
from app.models.models import User, UserPreference
from app.schemas.schemas import UserPreferencesOut, UserPreferencesUpdate

router = APIRouter(prefix="/preferences", tags=["preferences"])

REQUIRED_FEATURES = [
    "dashboard",
    "chat",
    "inventory",
    "shop",
    "social",
    "jobs",
    "calendar",
    "health",
    "home",
    "integrations",
    "vault",
    "settings",
    "profile",
]


def _ensure_all_features(prefs: UserPreference) -> bool:
    """Add any missing required features and return True if changes were made."""
    added = False
    for feature in REQUIRED_FEATURES:
        if feature not in prefs.enabled_features:
            prefs.enabled_features.append(feature)
            added = True
    return added


@router.get("", response_model=UserPreferencesOut)
def get_preferences(
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Get current user's preferences, creating default if missing. Ensures ALL features are enabled."""
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(
            user_id=current_user.id,
            theme_mode="system",
            theme_palette="teal",
            font_size="medium",
            enabled_features=list(REQUIRED_FEATURES),
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    else:
        if _ensure_all_features(prefs):
            db.commit()
            db.refresh(prefs)
    return prefs


@router.patch("", response_model=UserPreferencesOut)
def update_preferences(
    body: UserPreferencesUpdate,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Update current user's preferences."""
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(
            user_id=current_user.id,
            theme_mode="system",
            theme_palette="teal",
            font_size="medium",
            enabled_features=list(REQUIRED_FEATURES),
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(prefs, field, value)

    # Ensure enabled_features always contains all required keys
    if "enabled_features" in body.model_dump(exclude_unset=True):
        prefs.enabled_features = list(dict.fromkeys([
            *prefs.enabled_features,
            *REQUIRED_FEATURES,
        ]))
    else:
        _ensure_all_features(prefs)

    db.commit()
    db.refresh(prefs)
    return prefs
