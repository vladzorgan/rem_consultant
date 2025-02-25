from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Создаем синхронное соединение с базой данных
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE if hasattr(settings, "DB_POOL_SIZE") else 20,
    max_overflow=settings.DB_MAX_OVERFLOW if hasattr(settings, "DB_MAX_OVERFLOW") else 30,
    pool_timeout=30,
    pool_recycle=settings.DB_POOL_RECYCLE if hasattr(settings, "DB_POOL_RECYCLE") else 3600,
    echo=settings.SQL_ECHO if hasattr(settings, "SQL_ECHO") else False,
)

# Создаем асинхронное соединение для FastAPI
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE if hasattr(settings, "DB_POOL_SIZE") else 20,
    max_overflow=settings.DB_MAX_OVERFLOW if hasattr(settings, "DB_MAX_OVERFLOW") else 30,
    pool_recycle=settings.DB_POOL_RECYCLE if hasattr(settings, "DB_POOL_RECYCLE") else 3600,
    echo=settings.SQL_ECHO if hasattr(settings, "SQL_ECHO") else False,
)

# Создаем сессию для синхронного доступа
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем сессию для асинхронного доступа
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine
)

# Контекстный менеджер для синхронных операций
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Генератор для асинхронных операций (для FastAPI)
async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()