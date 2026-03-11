from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, Boolean, Numeric, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class User(Base):
    """
    Модель користувача.
    Зберігає дані про замовників, виконавців та адміністраторів.
    """
    __tablename__ = 'users'

    # 1. Ідентифікація
    # Використовуємо BigInteger, бо Telegram ID перевищують ліміт звичайного Integer.
    # autoincrement=False, бо ми самі задаємо ID (той, що дає Telegram).
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    # 2. Права доступу
    # role може бути 'user' або 'admin'.
    role: Mapped[str] = mapped_column(String(20), default='user')

    # Блокування та статус шахрая
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_scammer: Mapped[bool] = mapped_column(Boolean, default=False)

    # 3. Фінанси та Рейтинг
    # Numeric краще за Float для грошей (точні обчислення).
    # (10, 2) означає до 8 знаків до коми і 2 після (наприклад, 12345678.99).
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Рейтинг розраховується за формулою, але зберігається тут для швидкого доступу.
    rating: Mapped[float] = mapped_column(Float, default=0.0)

    # 4. Технічні поля (Аудит)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.telegram_id}, role={self.role}, rating={self.rating})>"