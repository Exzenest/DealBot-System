from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, DateTime, func,ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer

from src.database.base import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID

import enum



class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    from_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    to_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))

    score: Mapped[int] = mapped_column(Integer, nullable=False)

    comment: Mapped[str] = mapped_column(Text,nullable=False)

    agreement_id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True),ForeignKey("agreements.id",ondelete="CASCADE"))




    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())





    from_user = relationship(
        "User",
        foreign_keys=[from_user_id],
        lazy="joined"
    )

    agreement = relationship(
        "Agreement",
        foreign_keys=[agreement_id],
        lazy="joined"
    )

    to_user = relationship(
        "User",
        foreign_keys=[to_user_id],
        lazy="joined"
    )

