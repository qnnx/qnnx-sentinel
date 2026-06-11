from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "audit"}

    id = Column(UUID(as_uuid=True), primary_key=True)

    action = Column(Text, nullable=False)
    status = Column(Text)

    user_id = Column(UUID(as_uuid=True))
    api_key_id = Column(UUID(as_uuid=True))

    details = Column(JSONB)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
