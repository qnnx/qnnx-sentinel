from sqlalchemy import Column, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ApiUsage(Base):
    __tablename__ = "api_usage"
    __table_args__ = {"schema": "crypto"}

    id = Column(UUID(as_uuid=True), primary_key=True)

    endpoint = Column(Text, nullable=False)

    request_count = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )