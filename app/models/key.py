from sqlalchemy import Boolean, Column, DateTime, Text, text
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
    storage_mode = Column(Text, nullable=False, server_default=text("'customer_managed'"))
    private_key_exported = Column(Boolean, nullable=False, server_default=text("false"))

    expires_at = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
