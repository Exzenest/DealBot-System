from datetime import datetime
from decimal import Decimal
import enum
import uuid

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    func,
    ForeignKey,
    Numeric,
    Enum,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database.base import Base


class PostType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class PostStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"
    DONE = "done"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    author_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
    )

    executor_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # залишив для сумісності зі старим кодом
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type_enum"),
        nullable=False,
        default=PostType.PUBLIC,
    )

    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status_enum"),
        nullable=False,
        default=PostStatus.NEW,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    channel_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    author = relationship(
        "User",
        foreign_keys=[author_id],
        lazy="joined",
    )

    executor = relationship(
        "User",
        foreign_keys=[executor_id],
        lazy="joined",
    )

    def __repr__(self):
        return f"<Post id={self.id} title={self.title} status={self.status.value}>"