from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_api_key_id", "api_key_id"),
        Index("idx_audit_logs_created_at", "created_at"),
        {"schema": "audit"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True)

    event_type = Column(Text, nullable=False)
    resource_type = Column(Text)
    resource_id = Column(Text)
    status = Column(Text, nullable=False)

    user_id = Column(UUID(as_uuid=True))
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("public.api_keys.id", ondelete="SET NULL"))
    ip_address = Column(Text)

    details = Column(JSONB)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
