from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import contextmanager

# Базовый класс для всех моделей
Base = declarative_base()

# Настройка соединения с PostgreSQL
DATABASE_URL = "postgresql+psycopg2://root:password@api-postgres/repair_price_bot"
ASYNC_DATABASE_URL = "postgresql+asyncpg://root:password@api-postgres/repair_price_bot"

# Создаем синхронное соединение с базой данных
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
)

# Создаем асинхронное соединение для FastAPI
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_recycle=3600,
)

# Создаем сессию для синхронного доступа
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для создания таблиц (используйте ее только для разработки, в продакшне используйте Alembic)
def init_db():
    Base.metadata.create_all(bind=engine)

# Контекстный менеджер для синхронных операций
@contextmanager
def get_db_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Генератор для асинхронных операций (для FastAPI)
async def get_async_session():
    async with AsyncSession(async_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise