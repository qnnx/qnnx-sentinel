import uuid
from sqlalchemy import Column, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Algorithm(Base):
    __tablename__ = "algorithms"
    __table_args__ = {"schema": "crypto"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    algo_id = Column(Text, unique=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)
    type = Column(Text, nullable=False)
    security_level = Column(Text, nullable=False)
    nist_standard = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default=text("'active'"))
    recommended_use = Column(Text)
    description = Column(Text)
    algo_type = Column(Text)
    family = Column(Text)
    public_key_size = Column(Text)
    private_key_size = Column(Text)
    ciphertext_size = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )