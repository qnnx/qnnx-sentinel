from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "crypto"}

    id = Column(UUID(as_uuid=True), primary_key=True)

    action = Column(Text, nullable=False)

    actor_id = Column(UUID(as_uuid=True))

    details = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )