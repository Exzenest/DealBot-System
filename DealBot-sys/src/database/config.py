from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

import os

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = os.path.join(BASE_DIR, ".env")

print("ENV_PATH =", ENV_PATH)
print("ENV EXISTS =", os.path.exists(ENV_PATH))



class DbConfig(BaseSettings):
    """Налаштування бази даних SQLite"""

    name: str = str(BASE_DIR / "TasksDb.sqlite3")

    print("DBCONFIG FILE:", __file__)
    print("DB NAME RAW:", name)

    @property
    def url(self) -> str:
        """Async URL для SQLAlchemy"""
        return f"sqlite+aiosqlite:///{self.name}"

    @property
    def sync_url(self) -> str:
        """Sync URL для Alembic"""
        return f"sqlite:///{self.name}"


class RedisConfig(BaseSettings):
    """Налаштування Redis (для FSM та кешу)"""
    host: str = "localhost"
    port: int = 6379
    db_fsm: int = 0
    db_job: int = 1

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db_fsm}"


class BotConfig(BaseSettings):
    """Налаштування Telegram ботів"""
    token_main: SecretStr
    token_task: SecretStr
    admin_ids: list[int]
    channel_id: int

IS_ALEMBIC = os.environ.get("ALEMBIC", "0") == "1"
class Settings(BaseSettings):
    """Головний клас налаштувань"""
    db: DbConfig = DbConfig()
    redis: RedisConfig = RedisConfig()
    bot: BotConfig | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False
    )

    def load_bot(self) -> BotConfig:
        if self.bot is None:
            self.bot = BotConfig()
        return self.bot




# Settings(db = env.db)
config = Settings()
