import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base

class ProviderType(str, enum.Enum):
    STRIPE = "stripe"
    GITHUB = "github"
    SHOPIFY = "shopify"
    GENERIC = "generic"

class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    EXHAUSTED = "exhausted"

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    secret_key = Column(String(255), nullable=False)
    provider = Column(
        SQLEnum(ProviderType, name="provider_type", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProviderType.GENERIC
    )
    target_url = Column(String(1024), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    max_retries = Column(Integer, nullable=False, default=5)
    timeout_seconds = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False)
    provider = Column(
        SQLEnum(ProviderType, name="provider_type", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    event_type = Column(String(255), nullable=True)
    headers = Column(JSONB, nullable=False)
    payload = Column(JSONB, nullable=False)
    raw_body = Column(Text, nullable=False)
    signature_valid = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), primary_key=True, default=lambda: datetime.now(timezone.utc))

class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    event_created_at = Column(DateTime(timezone=True), nullable=False)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False)
    attempt_count = Column(Integer, nullable=False, default=1)
    status = Column(
        SQLEnum(DeliveryStatus, name="delivery_status", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DeliveryStatus.PENDING
    )
    response_status = Column(Integer, nullable=True)
    response_headers = Column(JSONB, nullable=True)
    response_body = Column(Text, nullable=True)
    execution_duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

