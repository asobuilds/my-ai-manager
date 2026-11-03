"""Mock Gmail integration for local development and testing without Google OAuth."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.integrations.base_connector import BaseConnector


class MockGmailConnector(BaseConnector):
    """Returns hardcoded messages so the system can run without real Google keys."""

    platform = "gmail"

    def fetch_messages(self) -> list[dict[str, Any]]:
        """Return a fixed set of fake Gmail messages."""
        return [
            {
                "external_id": "mock-gmail-001",
                "sender": "boss@company.com",
                "content": "Urgent: please review the quarterly report before tomorrow's meeting.",
                "subject": "Important Work Email",
                "received_at": datetime(2026, 11, 1, 9, 0, tzinfo=UTC),
            },
            {
                "external_id": "mock-gmail-002",
                "sender": "news@site.com",
                "content": "This week's top stories. Unsubscribe at any time.",
                "subject": "Newsletter",
                "received_at": datetime(2026, 11, 1, 12, 30, tzinfo=UTC),
            },
            {
                "external_id": "mock-gmail-003",
                "sender": "hr@tech.com",
                "content": "We are pleased to offer you the position. Please review the attached offer.",
                "subject": "Job Offer",
                "received_at": datetime(2026, 11, 2, 8, 15, tzinfo=UTC),
            },
        ]

    def send_reply(self, external_id: str, text: str) -> bool:
        """Pretend to send a reply, always succeeding."""
        return True
