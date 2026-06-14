import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Key(Base):
    __tablename__ = "keys"
    __table_args__ = (
        Index("idx_keys_user_id", "user_id"),
        Index("idx_keys_algorithm_id", "algorithm_id"),
        {"schema": "crypto"},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False)
    algorithm_id = Column(UUID(as_uuid=True), ForeignKey("crypto.algorithms.id", ondelete="CASCADE"), nullable=False)

    key_type = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default=text("'active'"))

    public_key = Column(Text, nullable=False)
    private_key_ref = Column(Text)
    storage_mode = Column(Text, nullable=False, server_default=text("'customer_managed'"))
    private_key_exported = Column(Boolean, nullable=False, server_default=text("false"))
    name = Column(Text)
    purpose = Column(Text)
    key_strength = Column(Text)

    expires_at = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user = relationship("User", foreign_keys=[user_id])
    algorithm = relationship("Algorithm", foreign_keys=[algorithm_id])
