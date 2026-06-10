from sqlalchemy import Column, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ApiUsage(Base):
    __tablename__ = "api_usage"
    __table_args__ = {"schema": "crypto"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    actor_id = Column(UUID(as_uuid=True))

    endpoint = Column(Text, nullable=False)
    http_method = Column(Text, nullable=False)
    algorithm = Column(Text)
    response_status = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)

    request_count = Column(Integer, default=1)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )