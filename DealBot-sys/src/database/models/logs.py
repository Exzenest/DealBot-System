from datetime import datetime


from sqlalchemy import BigInteger, String, DateTime, func,ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID


class Logs(Base):
    __tablename__ = 'logs'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    actor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))


    action: Mapped[str] = mapped_column(String(255),nullable=False)

    details: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor = relationship(
        "User",
        foreign_keys=[actor_id],
        lazy="joined"
    )


    def __repr__(self):
        return f"< id={self.id}, action={self.action}, user={self.actor.full_name}>"