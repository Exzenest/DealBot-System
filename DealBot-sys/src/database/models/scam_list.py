from datetime import datetime


from sqlalchemy import BigInteger, String, DateTime, func,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID


class Scammer(Base):
    
    __tablename__ = 'scam_list'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    user_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("users.telegram_id", ondelete="CASCADE"), autoincrement=False)

    added_by_admin_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("users.telegram_id", ondelete="SET NULL"), autoincrement=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)


    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined"
    )

    added_by_admin = relationship(
        "User",
        foreign_keys=[added_by_admin_id],
        lazy="joined"
    )

    def __repr__(self):
        return f"<Scammer user={self.user_id}, admin={self.added_by_admin_id}>"

