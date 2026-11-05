from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    phone: str | None
    location: str | None
    bio: str | None
    resume_text: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Connections ----------

class ConnectionCreate(BaseModel):
    provider: str  # gmail, linkedin, indeed
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None


class ConnectionOut(BaseModel):
    id: UUID
    provider: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConnectionStatus(BaseModel):
    gmail_connected: bool = False
    authorization_url: str | None = None


# ---------- Drafts ----------

class DraftCreate(BaseModel):
    subject: str | None = None
    body: str
    to: str | None = None
    cc: str | None = None
    bcc: str | None = None
    connection_id: UUID | None = None
    conversation_id: str | None = None
    original_message_id: str | None = None


class DraftUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None
    to: str | None = None
    cc: str | None = None
    bcc: str | None = None
    status: str | None = None


class DraftOut(BaseModel):
    id: UUID
    user_id: UUID
    connection_id: UUID | None
    subject: str | None
    body: str
    to: str | None
    cc: str | None
    bcc: str | None
    status: str
    conversation_id: str | None
    original_message_id: str | None
    created_at: datetime
    updated_at: datetime
    sent_at: datetime | None

    class Config:
        from_attributes = True


# ---------- Job Applications ----------

class JobApplicationCreate(BaseModel):
    company: str = Field(min_length=1)
    position: str = Field(min_length=1)
    company_name: str | None = None
    job_title: str | None = None
    job_url: str | None = None
    status: str = "saved"
    notes: str | None = None
    applied_date: datetime | None = None
    resume_used: str | None = None
    cover_letter: str | None = None
    applied_at: datetime | None = None
    follow_up_date: datetime | None = None


class JobApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    cover_letter: str | None = None
    follow_up_date: datetime | None = None
    company_name: str | None = None
    job_title: str | None = None
    applied_date: datetime | None = None


class JobApplicationOut(BaseModel):
    id: UUID
    user_id: UUID
    company: str
    position: str
    company_name: str | None
    job_title: str | None
    job_url: str | None
    status: str
    notes: str | None
    applied_date: datetime | None
    resume_used: str | None
    cover_letter: str | None
    applied_at: datetime | None
    follow_up_date: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- File Catalog ----------

class FileCatalogCreate(BaseModel):
    name: str = Field(min_length=1)
    path: str = Field(min_length=1)
    file_type: str | None = None
    size_bytes: int | None = None
    description: str | None = None
    tags: list[str] | None = None
    source: str | None = None
    message_id: str | None = None


class FileCatalogOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    path: str
    file_type: str | None
    size_bytes: int | None
    description: str | None
    tags: list[str] | None
    source: str | None
    message_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Chat ----------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None
    context_keys: list[str] | None = None  # e.g. ["gmail", "jobs"]


class ExplainRequest(BaseModel):
    message_id: str
    draft_text: str


# ---------- Profile ----------

class ProfileUpdate(BaseModel):
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    resume_text: str | None = None
