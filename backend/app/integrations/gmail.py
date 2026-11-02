"""Gmail integration module."""
from __future__ import annotations

import base64
from datetime import datetime
from email.mime.text import MIMEText
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import get_settings


class GmailConnector:
    """Handles all Gmail API interactions for a connected user."""

    def __init__(self, access_token: str, refresh_token: str | None = None):
        self._creds = Credentials(access_token, refresh_token=refresh_token)
        self._service = build("gmail", "v1", credentials=self._creds)

    def list_threads(self, query: str = "", max_results: int = 20) -> list[dict[str, Any]]:
        results = self._service.users().threads().list(userId="me", q=query, maxResults=max_results).execute()
        threads = results.get("threads", [])
        out = []
        for t in threads:
            msg = self._service.users().threads().get(userId="me", id=t["id"]).execute()
            snippet = msg["snippet"]
            first_msg = msg["messages"][0]
            headers = {h["name"]: h["value"] for h in first_msg.get("headers", [])}
            out.append({
                "thread_id": t["id"],
                "snippet": snippet,
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "message_count": msg.get("messageCount", 0),
            })
        return out

    def get_messages(self, thread_id: str, max_results: int = 20) -> list[dict[str, Any]]:
        msg_list = self._service.users().threads().get(userId="me", id=thread_id, format="FULL").execute()
        out = []
        for m in msg_list.get("messages", []):
            payload = m.get("payload", {})
            headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
            body = self._get_body(payload)
            out.append({
                "message_id": m.get("id"),
                "thread_id": thread_id,
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "date": headers.get("Date", ""),
                "body": body,
                "snippet": m.get("snippet", ""),
            })
        return out

    def send_draft(self, to: str, subject: str, body: str, cc: str | None = None, bcc: str | None = None) -> dict[str, str]:
        msg = MIMEText(body, "plain")
        msg["to"] = to
        msg["subject"] = subject
        if cc:
            msg["cc"] = cc
        if bcc:
            msg["bcc"] = bcc
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        sent = self._service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"message_id": sent["id"], "thread_id": sent.get("threadId")}

    def list_labels(self) -> list[dict[str, Any]]:
        results = self._service.users().labels().list(userId="me").execute()
        return results.get("labels", [])

    def add_label_to_thread(self, thread_id: str, label_ids: list[str]) -> dict:
        return self._service.users().threads().modify(
            userId="me", id=thread_id, body={"addLabelIds": label_ids}
        ).execute()

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
                return base64.urlsafe_b64encode(part["body"]["data"].encode()).decode()
            if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64encode(part["body"]["data"].encode()).decode()
        return ""
