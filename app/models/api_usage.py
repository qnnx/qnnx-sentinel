import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ApiUsage(Base):
    __tablename__ = "api_usage"
    __table_args__ = (
        Index("idx_api_usage_user_id", "user_id"),
        Index("idx_api_usage_api_key_id", "api_key_id"),
        Index("idx_api_usage_created_at", "created_at"),
        Index("idx_api_usage_operation", "operation"),
        {"schema": "analytics"},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id = Column(UUID(as_uuid=True))
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("public.api_keys.id", ondelete="SET NULL"))

    endpoint = Column(Text, nullable=False)
    method = Column(Text, nullable=False)
    operation = Column(Text, nullable=False)
    algorithm = Column(Text)
    response_status = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    success = Column(Boolean, nullable=False)
    ip_address = Column(Text)
    user_agent = Column(Text)
    error_type = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
