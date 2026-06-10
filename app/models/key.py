from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class Key(Base):
    __tablename__ = "keys"
    __table_args__ = {"schema": "crypto"}

    id = Column(UUID(as_uuid=True), primary_key=True)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    algorithm_id = Column(UUID(as_uuid=True), nullable=False)

    key_type = Column(Text, nullable=False)
    status = Column(Text, nullable=False)

    public_key = Column(Text, nullable=False)
    private_key_ref = Column(Text)

    expires_at = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )