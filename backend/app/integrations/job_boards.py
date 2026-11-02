"""Generic job board integration base."""
from __future__ import annotations

from typing import Any


class JobBoardConnector:
    """Base class for job board integrations (LinkedIn, Indeed, etc.)."""

    provider: str = "generic"

    def __init__(self, access_token: str, **kwargs: Any):
        self.access_token = access_token
        self._kwargs = kwargs

    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    def submit_application(self, job_id: str, resume_url: str, cover_letter: str | None = None) -> dict[str, Any]:
        raise NotImplementedError


class IndeedConnector(JobBoardConnector):
    provider = "indeed"

    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> list[dict[str, Any]]:
        # TODO: implement Indeed API integration
        raise NotImplementedError

    def submit_application(self, job_id: str, resume_url: str, cover_letter: str | None = None) -> dict[str, Any]:
        raise NotImplementedError


class LinkedInConnector(JobBoardConnector):
    provider = "linkedin"

    def search_jobs(self, query: str, location: str = "", limit: int = 20) -> list[dict[str, Any]]:
        # TODO: implement LinkedIn API integration
        raise NotImplementedError

    def submit_application(self, job_id: str, resume_url: str, cover_letter: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
