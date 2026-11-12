from datetime import datetime
from typing import Any
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
    role: str
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


# ---------- Suppliers ----------

class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = None


class SupplierOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    email: str | None
    phone: str | None
    created_at: datetime
    updated_at: datetime | None

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
    full_name: str | None = None
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    resume_text: str | None = None


# ---------- Shop / Inventory ----------

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    category: str | None = None
    price: int = Field(ge=0)  # in cents
    unit_type: str = Field(default="piece", max_length=50)
    units_per_carton: int = Field(ge=1, default=1)
    discount_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    stock_quantity: int = Field(ge=0, default=0)
    reorder_level: int = Field(ge=0, default=5)


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: int | None = Field(default=None, ge=0)
    unit_type: str | None = Field(default=None, max_length=50)
    units_per_carton: int | None = Field(default=None, ge=1)
    discount_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    stock_quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    id: UUID
    user_id: UUID
    sku: str
    name: str
    category: str | None
    price: int  # cents
    unit_type: str
    units_per_carton: int
    discount_percentage: float
    stock_quantity: int  # total base units
    reorder_level: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    movement_type: str = Field(pattern="^(in|out)$")
    quantity: int = Field(ge=1)
    original_unit: str | None = Field(default=None, max_length=20)  # "piece" or "carton"
    reason: str | None = None


class StockMovementResponse(BaseModel):
    id: UUID
    product_id: UUID
    movement_type: str
    quantity: int
    original_unit: str | None
    quantity_in_base_units: int
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Calendar ----------

class CalendarEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    event_type: str = Field(default="meeting", max_length=50)  # meeting, reminder, holiday


class CalendarEventOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    event_type: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


# ---------- Social Media ----------

class SocialPostCreate(BaseModel):
    platform: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)
    status: str = Field(default="draft", pattern="^(draft|scheduled|published)$")
    scheduled_time: datetime | None = None


class SocialPostUpdate(BaseModel):
    platform: str | None = Field(default=None, min_length=1, max_length=50)
    content: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, pattern="^(draft|scheduled|published)$")
    scheduled_time: datetime | None = None


class SocialPostOut(BaseModel):
    id: UUID
    user_id: UUID
    platform: str
    content: str
    status: str
    scheduled_time: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class SocialGenerateRequest(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    platform: str = Field(min_length=1, max_length=50)


# ---------- User Preferences ----------

class UserPreferencesOut(BaseModel):
    user_id: UUID
    theme_mode: str
    theme_palette: str
    font_size: str
    enabled_features: list[str]
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    theme_mode: str | None = None
    theme_palette: str | None = None
    font_size: str | None = None
    enabled_features: list[str] | None = None


# ---------- Health ----------

class HealthProfileCreate(BaseModel):
    blood_type: str | None = Field(default=None, max_length=10)
    genotype: str | None = Field(default=None, max_length=20)
    allergies: str | None = None
    medical_conditions: str | None = None


class HealthProfileOut(BaseModel):
    id: UUID
    user_id: UUID
    blood_type: str | None
    genotype: str | None
    allergies: str | None
    medical_conditions: str | None

    class Config:
        from_attributes = True


class HealthVitalsCreate(BaseModel):
    systolic: int | None = Field(default=None, ge=0)
    diastolic: int | None = Field(default=None, ge=0)
    heart_rate: int | None = Field(default=None, ge=0)
    weight: float | None = Field(default=None, ge=0)
    steps: int | None = Field(default=None, ge=0)
    calories: int | None = Field(default=None, ge=0)
    recorded_at: datetime | None = None


class HealthVitalsOut(BaseModel):
    id: UUID
    user_id: UUID
    systolic: int | None
    diastolic: int | None
    heart_rate: int | None
    weight: float | None
    steps: int | None
    calories: int | None
    recorded_at: datetime

    class Config:
        from_attributes = True


# ---------- Home Management ----------

class HomeAssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    serial_number: str | None = Field(default=None, max_length=255)
    purchase_date: datetime | None = None
    warranty_expiry: datetime | None = None


class HomeAssetOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    category: str
    serial_number: str | None
    purchase_date: datetime | None
    warranty_expiry: datetime | None

    class Config:
        from_attributes = True


class MaintenanceTaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime
    asset_id: UUID | None = None
    is_recurring: bool = False
    recurrence_days: int | None = Field(default=None, ge=1)
    is_completed: bool = False


class MaintenanceTaskOut(BaseModel):
    id: UUID
    user_id: UUID
    asset_id: UUID | None
    title: str
    description: str | None
    due_date: datetime
    is_recurring: bool
    recurrence_days: int | None
    is_completed: bool

    class Config:
        from_attributes = True


# ---------- Daily Report / Analytics ----------

class SalesSummary(BaseModel):
    total_revenue: float = 0.0
    top_products: list[dict[str, Any]] = Field(default_factory=list)
    avg_daily_sales: float = 0.0
    period_start: str | None = None
    period_end: str | None = None

    class Config:
        from_attributes = True


class DailyReportOut(BaseModel):
    id: UUID
    user_id: UUID
    report_text: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Secure Vault ----------

class VaultFileOut(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    encrypted_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class VaultDownloadRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)
