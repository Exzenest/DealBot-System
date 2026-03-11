from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.database.config import config

# 1. Створення двигуна (Engine)
# Це "серце" бази даних, яке керує пулом з'єднань.
engine = create_async_engine(
    url=config.db.url,
    # echo=True виводитиме всі SQL-запити в консоль.
    # Корисно для розробки, але на продакшені краще вимкнути (False).
    echo=True,
)

# 2. Фабрика сесій
# Ми не створюємо нове з'єднання кожен раз, а беремо сесію з пулу.
# expire_on_commit=False — критично для асинхронності.
# Це дозволяє звертатися до атрибутів об'єкта навіть після commit().
session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 3. Базовий клас для моделей
# Усі ваші моделі (User, Post, Agreement) будуть наслідувати цей клас.
# Це новий стиль SQLAlchemy 2.0.
class Base(DeclarativeBase):
    pass