from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, DateTime, func,ForeignKey, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID

import enum

class LogType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class AgreeStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class Agreement(Base):
    __tablename__ = 'agreements'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    performer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))

    post_id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True),ForeignKey("posts.id",ondelete="CASCADE"))


    type: Mapped[LogType] = mapped_column(
        Enum(LogType, name="log_type_enum"),
        nullable=False,
        default=LogType.PUBLIC
    )

    status: Mapped[AgreeStatus] = mapped_column(Enum(AgreeStatus,name="log_status_enum"),nullable=False, default=AgreeStatus.ACTIVE)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)



    customer = relationship(
        "User",
        foreign_keys=[customer_id],
        lazy="joined"
    )

    post = relationship(
        "Post",
        foreign_keys=[post_id],
        lazy="joined"
    )

    performer = relationship(
        "User",
        foreign_keys=[performer_id],
        lazy="joined"
    )

