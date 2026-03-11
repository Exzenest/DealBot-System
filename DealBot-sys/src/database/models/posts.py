from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, DateTime, func,ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID

import enum

class PostType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class PostStatus(enum.Enum):
    DRAFT = "draft"
    MODERATION = "moderation"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    WORKING = "working"

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))

    executor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))


    title: Mapped[str] = mapped_column(String(255),nullable=False)

    description: Mapped[str] = mapped_column(Text,nullable=False)

    category: Mapped[str] = mapped_column(String(255),nullable=False)


    budget: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="log_type_enum"),
        nullable=False,
        default=PostType.PUBLIC
    )

    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus,name="log_status_enum"),nullable=False, default=PostStatus.MODERATION)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    channel_message_id: Mapped[int] = mapped_column(BigInteger,nullable=False)

    author = relationship(
        "User",
        foreign_keys=[author_id],
        lazy="joined"
    )

    executor = relationship(
        "User",
        foreign_keys=[executor_id],
        lazy="joined"
    )

    def __repr__(self):
        author_name = self.author.full_name if self.author else "Unknown"
        return f"<Log id={self.id}, title={self.title}, author={author_name}>"