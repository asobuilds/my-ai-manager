"""Home Assistant integration — read entity states and call services."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

HASS_TIMEOUT_SECONDS: float = 5.0

TRACKED_ENTITIES: list[str] = ["light.living_room", "switch.generator"]


def is_configured() -> bool:
    """Return True when both the Home Assistant URL and token are set."""
    return bool(settings.HASS_URL and settings.HASS_TOKEN)


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.HASS_TOKEN}"}


def get_entity_state(entity_id: str) -> dict[str, Any] | None:
    """Fetch the current state of a Home Assistant entity.

    GET {HASS_URL}/api/states/{entity_id} with the long-lived access token.
    Returns the HA state payload, or None when the integration is not
    configured or the request fails (network error, 4xx/5xx, missing entity).
    """
    if not is_configured():
        return None
    url = f"{settings.HASS_URL.rstrip('/')}/api/states/{entity_id}"
    try:
        resp = httpx.get(url, headers=_auth_headers(), timeout=HASS_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        logger.warning("Home Assistant state fetch failed for %s: %s", entity_id, exc)
        return None


def call_service(domain: str, service: str, entity_id: str) -> dict[str, Any] | None:
    """Call a Home Assistant service for a single entity.

    POST {HASS_URL}/api/services/{domain}/{service} with body
    {"entity_id": entity_id}. Returns the service response payload, or None
    when the integration is not configured or the request fails.
    """
    if not is_configured():
        return None
    url = f"{settings.HASS_URL.rstrip('/')}/api/services/{domain}/{service}"
    headers = {**_auth_headers(), "Content-Type": "application/json"}
    try:
        resp = httpx.post(
            url,
            headers=headers,
            json={"entity_id": entity_id},
            timeout=HASS_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        logger.warning(
            "Home Assistant service %s.%s failed for %s: %s",
            domain,
            service,
            entity_id,
            exc,
        )
        return None
