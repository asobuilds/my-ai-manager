"""Abstract base connector for all platform integrations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Abstract base class for all platform connectors (Gmail, WhatsApp, etc.)."""

    platform: str = "unknown"

    @abstractmethod
    def fetch_messages(self) -> list[dict[str, Any]]:
        """Fetch recent messages from the platform.

        Returns a list of message dictionaries, each containing at minimum:
            - external_id: str (unique ID from the platform)
            - sender: str
            - content: str
            - received_at: datetime | None
        """
        ...

    @abstractmethod
    def send_reply(self, external_id: str, text: str) -> bool:
        """Send a reply to a message identified by external_id.

        Returns True if the reply was sent successfully, False otherwise.
        """
        ...
