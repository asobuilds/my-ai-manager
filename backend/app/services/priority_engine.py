"""Priority engine for categorizing and scoring ingested messages."""
from __future__ import annotations

from typing import Any

# Word lists for rule-based classification
_WORK_KEYWORDS = ("boss", "manager", "director", "ceo", "client", "customer",
                  "hr@", "recruiter", "interview", "offer", "salary")
_NEWSLETTER_KEYWORDS = ("unsubscribe", "newsletter", "digest", "roundup",
                        "weekly", "monthly", "promotional")
_SPAM_KEYWORDS = ("lottery", "winner", "prize", "viagra", "nigerian",
                  "click here", "free money")
_JOB_KEYWORDS = ("job", "career", "position", "hiring", "opening",
                 "apply", "resume", "cv")


def calculate_priority(message_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate priority score and category for a message using rule-based logic.

    Args:
        message_data: Dictionary with keys like 'sender', 'content', 'subject'.

    Returns:
        Dictionary with 'priority_score' (int) and 'category' (str).

    TODO: Replace with LLM-based classification once the API integration is ready.
        Example future call:
            result = await llm_client.classify(message_data)
            return {"priority_score": result.score, "category": result.category}
    """
    sender = (message_data.get("sender") or "").lower()
    content = (message_data.get("content") or "").lower()
    subject = (message_data.get("subject") or "").lower()
    combined = f"{sender} {content} {subject}"

    priority_score = 0
    category = "Other"

    if any(kw in combined for kw in _WORK_KEYWORDS):
        priority_score = max(priority_score, 10)
        category = "Work"

    if any(kw in combined for kw in _JOB_KEYWORDS):
        priority_score = max(priority_score, 8)
        if category not in ("Work",):
            category = "Job"

    if any(kw in combined for kw in _NEWSLETTER_KEYWORDS):
        priority_score = max(priority_score, 1)
        category = "Newsletter"

    if any(kw in combined for kw in _SPAM_KEYWORDS):
        priority_score = max(priority_score, 0)
        category = "Spam"

    return {"priority_score": priority_score, "category": category}
