import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ApiSecurityEvent(Base):
    __tablename__ = "api_security_events"
    __table_args__ = (
        Index("idx_api_security_events_user_id", "user_id"),
        Index("idx_api_security_events_api_key_id", "api_key_id"),
        Index("idx_api_security_events_event_type", "event_type"),
        Index("idx_api_security_events_created_at", "created_at"),
        {"schema": "public"},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id = Column(UUID(as_uuid=True))
    api_key_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.api_keys.id", ondelete="SET NULL"),
    )
    event_type = Column(Text, nullable=False)
    endpoint = Column(Text)
    method = Column(Text)
    ip_address = Column(Text)
    user_agent = Column(Text)
    details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
import uuid
