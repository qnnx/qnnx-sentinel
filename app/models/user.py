import uuid

from sqlalchemy import Column, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    full_name = Column(Text)
    role = Column(Text, nullable=False, server_default=text("'user'"))
    organization_name = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
import uuid
