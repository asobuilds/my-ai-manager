"""Gmail integration module."""
from __future__ import annotations

import base64
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.integrations.base_connector import BaseConnector


def get_gmail_service(access_token: str, refresh_token: str | None = None) -> Any:
    """Initialize and return a Gmail API service using stored tokens.

    Placeholder: in production this would fetch tokens from the database
    for the current user and handle token refresh.
    """
    creds = Credentials(access_token, refresh_token=refresh_token)
    return build("gmail", "v1", credentials=creds)


class GmailConnector(BaseConnector):
    """Handles all Gmail API interactions for a connected user."""

    platform = "gmail"

    def __init__(self, access_token: str, refresh_token: str | None = None):
        self._creds = Credentials(access_token, refresh_token=refresh_token)
        self._service = build("gmail", "v1", credentials=self._creds)

    def fetch_messages(self) -> list[dict[str, Any]]:
        """Fetch recent messages from Gmail."""
        results = self._service.users().messages().list(
            userId="me", maxResults=20
        ).execute()
        out = []
        for m in results.get("messages", []):
            msg = self._service.users().messages().get(
                userId="me", id=m["id"], format="FULL"
            ).execute()
            payload = msg.get("payload", {})
            headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
            body = self._get_body(payload)
            out.append({
                "external_id": m.get("id"),
                "sender": headers.get("From", ""),
                "content": body,
                "subject": headers.get("Subject", ""),
                "received_at": headers.get("Date"),
            })
        return out

    def send_reply(self, external_id: str, text: str) -> bool:
        """Send a reply to a Gmail message by external_id."""
        msg = self._service.users().messages().get(
            userId="me", id=external_id, format="FULL"
        ).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        raw = f"Reply-To: {headers.get('From', '')}\r\n" \
              f"To: {headers.get('From', '')}\r\n" \
              f"Subject: Re: {headers.get('Subject', '')}\r\n\r\n{text}"
        raw_bytes = raw.encode("utf-8")
        raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
        try:
            self._service.users().messages().send(
                userId="me", body={"raw": raw_b64}
            ).execute()
            return True
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def _get_body(payload: dict) -> str:
        parts = payload.get("parts", [])
        if not parts:
            data = payload.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            return ""
        for part in parts:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        return ""
