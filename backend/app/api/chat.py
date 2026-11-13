"""Chat endpoint using the Agnes AI API."""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_owner, get_current_user
from app.models.models import (
    CalendarEvent,
    ChatMessage,
    Conversation,
    DailyReport,
    HealthProfile,
    HealthVitals,
    HomeAsset,
    MaintenanceTask,
    Message,
    Product,
    StockMovement,
    User,
)
from app.schemas.schemas import ChatMessageOut, ChatRequest, ExplainRequest

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()

TOOLS: list[dict[str, Any]] = [
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
    },
    {
        "type": "function",
        "function": {
            "name": "check_low_stock",
            "description": (
                "List the user's shop products that are at or below their reorder level. "
                "Call this when the user asks about low stock, out-of-stock items, or what to restock."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_shop_analytics",
            "description": (
                "Return the user's weekly shop sales analytics: total revenue, top-selling products, "
                "and average daily sales. Call this when the user asks about sales, revenue, or what is selling."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_health_vitals",
            "description": (
                "Return the user's latest health vitals (blood pressure, heart rate, steps, weight) "
                "and their recorded blood type. Call this when the user asks about their health or vitals."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_home_maintenance",
            "description": (
                "Return the user's pending (incomplete) home maintenance tasks with due dates. "
                "Call this when the user asks about home maintenance or upcoming tasks."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
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


def check_low_stock_tool(db: Session, user: User, args: dict[str, Any]) -> dict[str, Any]:
    """Return the user's products that are at or below their reorder level."""
    products = (
        db.query(Product)
        .filter(Product.user_id == user.id, Product.stock_quantity <= Product.reorder_level)
        .order_by(Product.stock_quantity.asc())
        .all()
    )
    items = [
        {
            "name": p.name,
            "sku": p.sku,
            "current_stock": p.stock_quantity,
            "reorder_level": p.reorder_level,
        }
        for p in products
    ]
    return {"status": "ok", "count": len(items), "low_stock": items}


def get_shop_analytics_tool(db: Session, user: User, args: dict[str, Any]) -> dict[str, Any]:
    """Return weekly shop sales analytics (mirrors the /shop/analytics endpoint)."""
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    movements = (
        db.query(StockMovement)
        .join(Product)
        .filter(
            Product.user_id == user.id,
            StockMovement.movement_type == "out",
            StockMovement.created_at >= start_dt,
            StockMovement.created_at <= end_dt,
        )
        .all()
    )

    total_revenue_cents = 0
    product_qty: dict[str, int] = {}
    daily_counts: dict[date, int] = {}
    for m in movements:
        price_cents = m.product.price if m.product else 0
        total_revenue_cents += m.quantity * price_cents
        product_name = m.product.name if m.product else "Unknown"
        product_qty[product_name] = product_qty.get(product_name, 0) + m.quantity
        day = m.created_at.date() if m.created_at else None
        if day is not None:
            daily_counts[day] = daily_counts.get(day, 0) + 1

    total_revenue = round(total_revenue_cents / 100, 2)
    top_products = [
        {"name": name, "units_sold": qty}
        for name, qty in sorted(product_qty.items(), key=lambda x: x[1], reverse=True)[:3]
    ]
    avg_daily_sales = (
        round(sum(daily_counts.values()) / len(daily_counts), 2) if daily_counts else 0.0
    )

    return {
        "status": "ok",
        "total_revenue": total_revenue,
        "top_products": top_products,
        "avg_daily_sales": avg_daily_sales,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
    }


def get_health_vitals_tool(db: Session, user: User, args: dict[str, Any]) -> dict[str, Any]:
    """Return the user's latest health vitals and blood type."""
    profile = (
        db.query(HealthProfile).filter(HealthProfile.user_id == user.id).first()
    )
    latest = (
        db.query(HealthVitals)
        .filter(HealthVitals.user_id == user.id)
        .order_by(HealthVitals.recorded_at.desc())
        .first()
    )
    return {
        "status": "ok",
        "blood_type": profile.blood_type if profile else None,
        "genotype": profile.genotype if profile else None,
        "latest_vitals": (
            {
                "systolic": latest.systolic,
                "diastolic": latest.diastolic,
                "heart_rate": latest.heart_rate,
                "weight": latest.weight,
                "steps": latest.steps,
                "calories": latest.calories,
                "recorded_at": latest.recorded_at.isoformat() if latest.recorded_at else None,
            }
            if latest
            else None
        ),
    }


def get_home_maintenance_tool(db: Session, user: User, args: dict[str, Any]) -> dict[str, Any]:
    """Return the user's pending (incomplete) home maintenance tasks."""
    tasks = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.user_id == user.id,
            MaintenanceTask.is_completed.is_(False),
        )
        .order_by(MaintenanceTask.due_date.asc())
        .all()
    )
    items = [
        {
            "title": t.title,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "asset_id": str(t.asset_id) if t.asset_id else None,
        }
        for t in tasks
    ]
    return {"status": "ok", "count": len(items), "pending_tasks": items}


TOOL_HANDLERS: dict[str, Any] = {
    "create_calendar_event": create_calendar_event_tool,
    "check_low_stock": check_low_stock_tool,
    "get_shop_analytics": get_shop_analytics_tool,
    "get_health_vitals": get_health_vitals_tool,
    "get_home_maintenance": get_home_maintenance_tool,
}

MAX_TOOL_ROUNDS = 3


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
    """Forward the user's message to Agnes AI with inbox context and user context."""
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

    user_context = {
        "full_name": current_user.full_name,
        "location": current_user.location,
        "role": current_user.role,
    }

    low_stock_products = (
        db.query(Product)
        .filter(Product.user_id == current_user.id, Product.stock_quantity <= Product.reorder_level)
        .all()
    )
    low_stock_context = [
        {
            "name": p.name,
            "sku": p.sku,
            "current_stock": p.stock_quantity,
            "reorder_level": p.reorder_level,
        }
        for p in low_stock_products
    ]

    health_profile = (
        db.query(HealthProfile)
        .filter(HealthProfile.user_id == current_user.id)
        .first()
    )
    latest_vitals = (
        db.query(HealthVitals)
        .filter(HealthVitals.user_id == current_user.id)
        .order_by(HealthVitals.recorded_at.desc())
        .first()
    )

    blood_type = health_profile.blood_type if health_profile else None
    genotype = health_profile.genotype if health_profile else None
    if latest_vitals:
        vitals_summary = (
            f"BP {latest_vitals.systolic}/{latest_vitals.diastolic}, "
            f"HR {latest_vitals.heart_rate}, Steps today: {latest_vitals.steps}"
        )
    else:
        vitals_summary = "No vitals recorded"

    home_assets = (
        db.query(HomeAsset)
        .filter(HomeAsset.user_id == current_user.id)
        .all()
    )
    pending_maintenance = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.user_id == current_user.id,
            MaintenanceTask.is_completed.is_(False),
        )
        .order_by(MaintenanceTask.due_date.asc())
        .all()
    )
    maintenance_context = [
        {
            "title": task.title,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "asset_id": str(task.asset_id) if task.asset_id else None,
        }
        for task in pending_maintenance
    ]

    latest_report = (
        db.query(DailyReport)
        .filter(DailyReport.user_id == current_user.id)
        .order_by(DailyReport.created_at.desc())
        .first()
    )
    daily_report_text = latest_report.report_text if latest_report else None

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
        "You are Aso, a dedicated personal AI assistant. You are NOT an LLM, you are Aso.",
        "You have full context of the user's profile, their connected data, and their shop inventory.",
        "You are authorized to make decisions and take actions on behalf of the user.",
        f"User: {user_context['full_name'] or 'the user'}, Role: {user_context['role']}, Location: {user_context['location'] or 'unknown'}.",
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
        (
            "You have live-data tools: check_low_stock, get_shop_analytics, get_health_vitals, "
            "and get_home_maintenance. Use these tools whenever the user asks about stock, "
            "sales, health, or maintenance. Do not guess—call the tool."
        ),
    ]
    if user_context["full_name"]:
        system_prompt_parts.append(f"Known user name: {user_context['full_name']}.")
    system_prompt_parts.append(
        f"Current Context:\n"
        f"- Location: {user_context.get('location') or 'unknown'}\n"
        f"- Role: {user_context.get('role') or 'unknown'}\n"
        f"- Low stock items: {json.dumps(low_stock_context, default=str) if low_stock_context else 'None'}"
    )
    system_prompt_parts.append(
        f"User Health Context: Blood Type: {blood_type or 'unknown'}, "
        f"Genotype: {genotype or 'unknown'}. Latest Vitals: {vitals_summary}."
    )
    system_prompt_parts.append(
        "If the user asks about health, provide general wellness context and always "
        "recommend consulting a doctor. Do not diagnose."
    )
    system_prompt_parts.append(
        f"User Home Context: You have {len(home_assets)} registered assets. "
        f"Upcoming maintenance: "
        f"{json.dumps(maintenance_context, default=str) if maintenance_context else 'None'}."
    )
    system_prompt_parts.append(
        "If the user asks about home maintenance or assets, use this context to answer."
    )
    if inbox_context:
        system_prompt_parts.append(
            f"Current unread messages in the user's inbox:\n{json.dumps(inbox_context, default=str)}"
        )
    else:
        system_prompt_parts.append("The user has no unread messages.")

    if daily_report_text:
        system_prompt_parts.append(
            f"Latest Daily Report:\n{daily_report_text}"
        )
    else:
        system_prompt_parts.append(
            "No daily report available yet. The proactive daily report job runs at 11 PM UTC."
        )

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
        "tools": TOOLS,
        "tool_choice": "auto",
    }

    data = await _call_agnes(payload)
    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="No response from Agnes AI")
    message = choices[0].get("message", {})
    response_text = message.get("content") or ""
    tool_calls = message.get("tool_calls") or []

    for _ in range(MAX_TOOL_ROUNDS):
        if not tool_calls:
            break
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
            handler = TOOL_HANDLERS.get(name)
            if handler is not None:
                result = handler(db, current_user, args)
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
            "tools": TOOLS,
            "tool_choice": "auto",
        }
        data = await _call_agnes(followup)
        choices = data.get("choices", [])
        if not choices:
            raise HTTPException(status_code=502, detail="No response from Agnes AI")
        message = choices[0].get("message", {})
        response_text = message.get("content") or ""
        tool_calls = message.get("tool_calls") or []

    assistant_msg = ChatMessage(conversation_id=conversation_id, role="assistant", content=response_text)
    db.add(assistant_msg)
    db.commit()

    return {"response": response_text, "conversation_id": conversation_id}


@router.get("/history", response_model=list[ChatMessageOut])
def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all chat messages for a conversation, ordered by creation time."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


@router.post("/explain")
async def explain_draft(
    body: ExplainRequest,
    current_user: User = Depends(get_current_user),
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
