from sqlalchemy import Boolean, Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ApiUsage(Base):
    __tablename__ = "api_usage"
    __table_args__ = {"schema": "analytics"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True))
    api_key_id = Column(UUID(as_uuid=True))

    endpoint = Column(Text, nullable=False)
    method = Column(Text, nullable=False)
    operation = Column(Text)
    algorithm = Column(Text)
    response_status = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    success = Column(Boolean)
    error_type = Column(Text)

    request_count = Column(Integer, default=1)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
