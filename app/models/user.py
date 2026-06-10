from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)

    full_name = Column(Text)
    role = Column(Text, nullable=False)
    organization_name = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )