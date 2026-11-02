import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Draft, UserConnection
from app.schemas.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat(body: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Conversational endpoint. Collects relevant context from connected sources
    and returns an AI-generated response.
    """
    # Gather context from user's data
    context: dict[str, object] = {}

    # Gmail threads
    gmail_conn = db.query(UserConnection).filter(
        UserConnection.user_id == current_user.id,
        UserConnection.provider == "gmail",
        UserConnection.is_active == True,
    ).first()
    if gmail_conn:
        recent_drafts = db.query(Draft).filter(
            Draft.user_id == current_user.id,
            Draft.status == "draft",
        ).limit(10).all()
        context["active_drafts"] = [
            {"id": str(d.id), "subject": d.subject, "body_preview": d.body[:200]}
            for d in recent_drafts
        ]

    # Job applications
    from app.models.models import JobApplication
    jobs = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
    ).limit(20).all()
    context["job_applications"] = [
        {"company": j.company, "position": j.position, "status": j.status}
        for j in jobs
    ]

    # Pass context to the AI layer (placeholder — wired to OpenCode later)
    prompt = body.message
    if body.context_keys:
        relevant = {k: context.get(k) for k in body.context_keys if k in context}
        prompt = f"Context:\n{json.dumps(relevant, default=str)}\n\nUser: {prompt}"

    # TODO: integrate with OpenCode/Agnes for real response generation
    response_text = f"[AI assistant] Received: {prompt}"

    return {"response": response_text, "conversation_id": body.conversation_id}
