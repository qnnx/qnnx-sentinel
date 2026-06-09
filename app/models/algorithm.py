from sqlalchemy import Column, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Algorithm(Base):
    __tablename__ = "algorithms"
    __table_args__ = {"schema": "crypto"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    algo_id = Column(Text, unique=True, nullable=False)

    name = Column(Text, unique=True, nullable=False)
    type = Column(Text, nullable=False)

    security_level = Column(Integer, nullable=False)

    nist_standard = Column(Text, nullable=False)

    status = Column(Text, nullable=False, default="active")

    recommended_use = Column(Text)

    description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
