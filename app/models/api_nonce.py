from sqlalchemy import Column, DateTime, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ApiNonce(Base):
    __tablename__ = "api_nonces"
    __table_args__ = (
        UniqueConstraint("api_key_id", "nonce", name="uq_api_nonces_api_key_id_nonce"),
        Index("idx_api_nonces_api_key_id", "api_key_id"),
        Index("idx_api_nonces_created_at", "created_at"),
        {"schema": "public"},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    api_key_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    nonce = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())