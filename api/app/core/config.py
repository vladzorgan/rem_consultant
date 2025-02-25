import os
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Основные настройки API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Repair Price API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "0.1.0"

    # Настройки для CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Настройки базы данных
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "root")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "repair_price_bot")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)
    ASYNC_DATABASE_URL: Optional[str] = None

    # Настройки пула соединений
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "False").lower() == "true"

    # Настройки JWT для авторизации (будут нужны для веб-интерфейса)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней

    # Настройки пагинации
    DEFAULT_PAGINATION_LIMIT: int = 20
    MAX_PAGINATION_LIMIT: int = 100

    # Настройки парсера
    PARSER_INTERVAL_MINUTES: int = 60  # Запуск каждый час

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные поля

    def __init__(self, **data):
        super().__init__(**data)

        # Используем DATABASE_URL из переменных окружения, если он указан
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Формируем асинхронный URL из основного URL
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql+psycopg2://"):
            self.ASYNC_DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql+psycopg2://", "postgresql+asyncpg://"
            )
        else:
            self.ASYNC_DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )


settings = Settings()