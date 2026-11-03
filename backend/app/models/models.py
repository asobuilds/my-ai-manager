import json
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    connections = relationship("UserConnection", back_populates="user", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="user", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    files = relationship("FileCatalog", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = ()


class UserConnection(Base):
    __tablename__ = "user_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # gmail, linkedin, indeed, etc.
    provider_user_id = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="connections")

    __table_args__ = (
        Index("ix_user_connections_user_id", "user_id"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)  # gmail, whatsapp, linkedin, etc.
    external_id = Column(String(255), nullable=False)
    sender = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    received_at = Column(DateTime, nullable=True)
    priority_score = Column(Integer, default=0)
    category = Column(String(50), nullable=True)
    status = Column(String(30), default="unread")  # unread, draft_ready, replied, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="messages")

    __table_args__ = (
        UniqueConstraint("user_id", "external_id", "platform", name="uq_user_platform_external_id"),
        Index("ix_messages_user_id", "user_id"),
        Index("ix_messages_platform", "platform"),
        Index("ix_messages_status", "status"),
        Index("ix_messages_priority", "priority_score"),
    )


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("user_connections.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    to = Column(Text, nullable=True)
    cc = Column(Text, nullable=True)
    bcc = Column(Text, nullable=True)
    status = Column(String(20), default="draft")  # draft, sent, failed
    conversation_id = Column(String(255), nullable=True)
    original_message_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="drafts")

    __table_args__ = (
        Index("ix_drafts_user_id", "user_id"),
        Index("ix_drafts_status", "status"),
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    job_url = Column(String(500), nullable=True)
    status = Column(String(30), default="applied")  # saved, applied, interview, offer, rejected
    notes = Column(Text, nullable=True)
    resume_used = Column(String(255), nullable=True)
    cover_letter = Column(Text, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="job_applications")

    __table_args__ = (
        Index("ix_job_applications_user_id", "user_id"),
        Index("ix_job_applications_status", "status"),
    )


class FileCatalog(Base):
    __tablename__ = "file_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(500), nullable=False)
    path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array as text
    source = Column(String(50), nullable=True)  # gmail, manual, import
    message_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="files")

    @property
    def tags(self):
        if self._tags is None:
            return None
        return json.loads(self._tags)

    @tags.setter
    def tags(self, value):
        if value is None:
            self._tags = None
        else:
            self._tags = json.dumps(value)

    @property
    def tags_list(self):
        return self.tags

    @property
    def tags(self):
        if self._tags is None:
            return None
        return json.loads(self._tags)

    @tags.setter
    def tags(self, value):
        if value is None:
            self._tags = None
        else:
            self._tags = json.dumps(value)

    __table_args__ = (
        Index("ix_file_catalog_user_id", "user_id"),
    )
