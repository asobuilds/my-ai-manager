"""Chat endpoint using the Agnes AI API."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_owner
from app.models.models import CalendarEvent, ChatMessage, Conversation, Message, User
from app.schemas.schemas import ChatRequest, ExplainRequest

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()

CALENDAR_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": (
                "Create an event on the user's calendar. Only call this when the user has "
                "explicitly asked to schedule/create an event and has provided enough detail "
                "(title, date, and time). Set confirm=true only for explicit scheduling requests."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short event title."},
                    "description": {"type": "string", "description": "Optional details."},
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO 8601 format, e.g. 2026-11-10T14:00:00.",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO 8601 format, e.g. 2026-11-10T15:00:00.",
                    },
                    "event_type": {
                        "type": "string",
                        "enum": ["meeting", "reminder", "holiday"],
                        "description": "Category of the event.",
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "True only when the user explicitly asked to schedule the event.",
                    },
                },
                "required": ["title", "start_time", "end_time", "confirm"],
            },
        },
    }
]


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def create_calendar_event_tool(
    db: Session, user: User, args: dict[str, Any]
) -> dict[str, Any]:
    """Execute the create_calendar_event AI tool.

    Writes require explicit user approval, so nothing is persisted unless the
    model sets ``confirm`` to true (which the system prompt ties to an explicit
    user scheduling request).
    """
    if not args.get("confirm"):
        return {
            "status": "confirmation_required",
            "message": "Ask the user to confirm before creating this event.",
        }

    title = (args.get("title") or "").strip()
    if not title:
        return {"status": "error", "message": "A title is required."}
    try:
        start = _parse_dt(args["start_time"])
        end = _parse_dt(args["end_time"])
    except (KeyError, TypeError, ValueError):
        return {"status": "error", "message": "start_time and end_time must be valid ISO 8601 datetimes."}

    if end <= start:
        return {"status": "error", "message": "end_time must be after start_time."}

    event = CalendarEvent(
        user_id=user.id,
        title=title,
        description=args.get("description"),
        start_time=start,
        end_time=end,
        event_type=args.get("event_type") or "meeting",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {
        "status": "created",
        "id": str(event.id),
        "title": event.title,
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "event_type": event.event_type,
    }


async def _call_agnes(payload: dict[str, Any]) -> dict[str, Any]:
    base_url = settings.AGNES_BASE_URL.rstrip("/")
    url = base_url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
    except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI API error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI request failed: {exc}")


@router.post("")
@router.post("/")
async def chat(body: ChatRequest, current_user: User = Depends(get_current_owner), db: Session = Depends(get_db)):
    """Forward the user's message to Agnes AI with inbox context."""
    unread_messages = (
        db.query(Message)
        .filter(Message.user_id == current_user.id, Message.status == "unread")
        .all()
    )
    inbox_context: list[dict[str, Any]] = [
        {
            "sender": m.sender,
            "subject": getattr(m, "subject", None),
            "content": m.content,
            "received_at": m.received_at.isoformat() if m.received_at else None,
            "priority_score": m.priority_score,
            "category": m.category,
        }
        for m in unread_messages
    ]

    if not body.conversation_id:
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(id=conversation_id, user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    else:
        conversation_id = body.conversation_id
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    now = datetime.now()
    system_prompt_parts = [
        "You are Aso, a personal AI assistant. Never identify as Agnes or an LLM. Always refer to yourself as Aso.",
        (
            "You can manage the user's calendar with the create_calendar_event tool. "
            f"The current local date and time is {now.isoformat(timespec='minutes')}. "
            "Resolve relative dates like 'tomorrow' or 'next Monday' against that. "
            "When the user explicitly asks to schedule or create an event, call "
            "create_calendar_event with confirm=true, choosing sensible start/end times "
            "(default to a 1-hour meeting if no duration is given). If key details are "
            "missing or the request is ambiguous, ask a clarifying question instead of "
            "calling the tool. After creating an event, confirm it back to the user."
        ),
    ]
    if inbox_context:
        system_prompt_parts.append(
            f"Current unread messages in the user's inbox:\n{json.dumps(inbox_context, default=str)}"
        )
    else:
        system_prompt_parts.append("The user has no unread messages.")

    messages_history: list[dict[str, Any]] = [
        {"role": "system", "content": "\n".join(system_prompt_parts)}
    ]

    if body.conversation_id:
        prior_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        for m in prior_messages:
            messages_history.append({"role": m.role, "content": m.content})

    messages_history.append({"role": "user", "content": body.message})

    user_msg = ChatMessage(conversation_id=conversation_id, role="user", content=body.message)
    db.add(user_msg)
    db.commit()

    payload = {
        "model": "agnes-2.5-flash",
        "messages": messages_history,
        "tools": CALENDAR_TOOLS,
        "tool_choice": "auto",
    }

    data = await _call_agnes(payload)
    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="No response from Agnes AI")
    message = choices[0].get("message", {})
    response_text = message.get("content") or ""

    tool_calls = message.get("tool_calls") or []
    if tool_calls:
        messages_history.append(
            {
                "role": "assistant",
                "content": message.get("content") or "",
                "tool_calls": tool_calls,
            }
        )
        for call in tool_calls:
            function = call.get("function", {}) or {}
            name = function.get("name")
            try:
                args = json.loads(function.get("arguments") or "{}")
            except (TypeError, ValueError):
                args = {}
            if name == "create_calendar_event":
                result = create_calendar_event_tool(db, current_user, args)
            else:
                result = {"status": "error", "message": f"Unknown tool: {name}"}
            messages_history.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": json.dumps(result, default=str),
                }
            )

        followup = {
            "model": "agnes-2.5-flash",
            "messages": messages_history,
            "tools": CALENDAR_TOOLS,
            "tool_choice": "auto",
        }
        data = await _call_agnes(followup)
        choices = data.get("choices", [])
        if not choices:
            raise HTTPException(status_code=502, detail="No response from Agnes AI")
        response_text = choices[0].get("message", {}).get("content") or ""

    assistant_msg = ChatMessage(conversation_id=conversation_id, role="assistant", content=response_text)
    db.add(assistant_msg)
    db.commit()

    return {"response": response_text, "conversation_id": conversation_id}


@router.post("/explain")
async def explain_draft(
    body: ExplainRequest,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """Explain why the AI wrote a specific draft reply, citing the original email."""
    msg = db.query(Message).filter(
        Message.id == uuid.UUID(body.message_id),
        Message.user_id == current_user.id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    system_prompt = (
        "You are Aso, a personal AI assistant. Never identify as Agnes or an LLM. "
        "Always refer to yourself as Aso. "
        "Your job is to explain WHY you wrote a draft reply the way you did. "
        "Reference specific details from the original email to justify your word choices, tone, and structure."
    )
    user_prompt = (
        f"Original email:\n"
        f"  From: {msg.sender or '(unknown)'}\n"
        f"  Subject: {getattr(msg, 'subject', None) or '(no subject)'}\n"
        f"  Content:\n{msg.content or '(no content)'}\n\n"
        f"Draft reply I generated:\n{body.draft_text}\n\n"
        f"Explain in 2-4 sentences why you wrote this draft — what cues from the original email influenced your word choice, tone, and structure?"
    )

    base_url = settings.AGNES_BASE_URL.rstrip("/")
    url = base_url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI API error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agnes AI request failed: {exc}")

    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="No response from Agnes AI")
    explanation = choices[0].get("message", {}).get("content", "")

    return {"explanation": explanation}
