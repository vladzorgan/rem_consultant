import enum

from sqlalchemy import Index, JSON, Boolean, Enum, Text, DECIMAL, Table
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

# Настройка соединения с PostgreSQL
DATABASE_URL = "postgresql+psycopg2://root:password@api-postgres/repair_price_bot"


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # Уникальность имени региона

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    __table_args__ = (
        Index('idx_region_name', 'name'),  # Индекс для быстрого поиска
    )

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    population = Column(Integer, default=0)
    users = relationship("User", back_populates="city")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    __table_args__ = (
        Index('idx_city_region_id', 'region_id'),  # Индекс для фильтрации по региону
    )

class ServiceCenter(Base):
    __tablename__ = "service_centers"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    city = relationship("City")
    user = relationship("User", back_populates="service_centers")
    addresses = relationship("ServiceCenterAddress", back_populates="service_center", cascade="all, delete-orphan")
    links = relationship("ServiceCenterLink", back_populates="service_center", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="service_center", cascade="all, delete-orphan")
    prices = relationship("Price", back_populates="service_center", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_service_center_city_id', 'city_id'),  # Индекс для фильтрации по городу
    )

class AddServiceRequest(Base):
    __tablename__ = "service_claim_requests"

    id = Column(Integer, primary_key=True, index=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    message = Column(String, nullable=False)  # Сообщение от пользователя
    contact = Column(String, nullable=False)  # Контакт для связи (например, телефон или email)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    service_center = relationship("ServiceCenter")
    user = relationship("User")

    __table_args__ = (
        Index('idx_service_claim_service_center_id', 'service_center_id'),
        Index('idx_service_claim_telegram_id', 'telegram_id'),
    )

class ServiceCenterAddress(Base):
    __tablename__ = "service_center_addresses"

    id = Column(Integer, primary_key=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    service_center = relationship("ServiceCenter", back_populates="addresses")

class ServiceCenterLink(Base):
    __tablename__ = "service_center_links"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)  # Например, "website", "telegram"
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    link = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    service_center = relationship("ServiceCenter", back_populates="links")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    author = Column(String, nullable=False)
    rating = Column(Float, nullable=True)  # Может быть опциональным
    text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    service_center = relationship("ServiceCenter", back_populates="reviews")

    __table_args__ = (
        Index('idx_review_service_center_id', 'service_center_id'),  # Индекс для фильтрации отзывов
    )

class DeviceBrand(Base):
    __tablename__ = "device_brands"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    models = relationship("DeviceModel", back_populates="brand", cascade="all, delete-orphan")

class DeviceModel(Base):
    __tablename__ = "device_models"

    id = Column(Integer, primary_key=True)
    device_brand_id = Column(Integer, ForeignKey('device_brands.id'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, default="smartphone", nullable=False)

    brand = relationship("DeviceBrand", back_populates="models")
    repairs = relationship("ModelRepair", back_populates="model")  # Оставляем как есть
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    __table_args__ = (
        Index('idx_device_model_brand_id', 'device_brand_id'),
    )

class ModelRepair(Base):
    __tablename__ = 'model_repairs'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('device_models.id'), nullable=False)
    repair_type_id = Column(Integer, ForeignKey('repair_types.id'), nullable=False)
    complexity = Column(String(50), nullable=True)
    model = relationship('DeviceModel', back_populates='repairs')
    repair_type = relationship('RepairType', back_populates='model_repairs')

    def __repr__(self):
        return f"<ModelRepair(model_id={self.model_id}, repair_type_id={self.repair_type_id})>"

repair_type_repair = Table(
    'repair_type_repair',
    Base.metadata,
    Column('repair_id', Integer, ForeignKey('repairs.id'), primary_key=True),
    Column('repair_type_id', Integer, ForeignKey('repair_types.id'), primary_key=True)
)

class RepairType(Base):
    __tablename__ = 'repair_types'

    id = Column(Integer, primary_key=True)
    group_name = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Связи
    model_repairs = relationship('ModelRepair', back_populates='repair_type')
    repair_parts = relationship('RepairPart', back_populates='repair_type')
    repairs = relationship('Repair', secondary=repair_type_repair, back_populates='repair_types')

    def __repr__(self):
        return f"<RepairType(name='{self.name}')>"

class Repair(Base):
    __tablename__ = 'repairs'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Связь с RepairType через связующую таблицу
    repair_types = relationship('RepairType', secondary=repair_type_repair, back_populates='repairs')

    def __repr__(self):
        return f"<Repair(name='{self.name}')>"

class Part(Base):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    retail_price = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=True)

    # Связь с repair_parts
    repair_parts = relationship('RepairPart', back_populates='part')

    def __repr__(self):
        return f"<Part(name='{self.name}', retail_price={self.retail_price})>"

class RepairPart(Base):
    __tablename__ = 'repair_parts'

    id = Column(Integer, primary_key=True)
    repair_type_id = Column(Integer, ForeignKey('repair_types.id'), nullable=False)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    # Связи
    repair_type = relationship('RepairType', back_populates='repair_parts')
    part = relationship('Part', back_populates='repair_parts')

    def __repr__(self):
        return f"<RepairPart(repair_type_id={self.repair_type_id}, part_id={self.part_id}, quantity={self.quantity})>"

class RepairPrice(Base):
    __tablename__ = "repair_prices"

    id = Column(Integer, primary_key=True)

    device_model_id = Column(Integer, ForeignKey('device_models.id'), nullable=False)
    repair_id = Column(Integer, ForeignKey('repairs.id'), nullable=False)  # Ссылка на таблицу repairs
    price = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Связи
    device_model = relationship("DeviceModel")
    repair = relationship("Repair")  # Ссылка на модель Repair

    __table_args__ = (
        Index('idx_repair_price_device_model_id', 'device_model_id'),
        Index('idx_repair_price_repair_id', 'repair_id'),
    )

    def __repr__(self):
        return f"<RepairPrice(id={self.id}, repair_id={self.repair_id}, price={self.price})>"

class PriceAnalytic(Base):
    __tablename__ = "price_analytics"

    id = Column(Integer, primary_key=True)
    repair_price_id = Column(Integer, ForeignKey('repair_prices.id'), nullable=False)  # Ссылка на repair_prices
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)  # Добавлено

    price = Column(Float, nullable=False)
    change_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Связи (опционально, если нужны)
    repair_price = relationship("RepairPrice", back_populates="history")
    service_center = relationship("ServiceCenter")

    def __repr__(self):
        return f"<PriceAnalytic(id={self.id}, price_id={self.price_id}, old_price={self.old_price}, new_price={self.new_price})>"


class BotLog(Base):
    __tablename__ = "bot_logs"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, nullable=False)
    request_text = Column(String, nullable=False)
    response_text = Column(JSON, nullable=False)  # JSON для сложных ответов
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    __table_args__ = (
        Index('idx_bot_log_telegram_user_id', 'telegram_user_id'),  # Индекс для фильтрации по пользователю
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    city = relationship("City", back_populates="users")
    service_centers = relationship("ServiceCenter", back_populates="user")

    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),  # Уникальный индекс для поиска по telegram_id
    )

# Инициализация базы данных
from app.database import engine, init_db

# Вызов init_db можно сделать при импорте или в точке входа приложения
if __name__ == "__main__":
    init_db()  # Создаёт таблицы при запуске models.py напрямую (для тестов)

# Создаем соединение с базой данных
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Увеличиваем размер пула
    max_overflow=30,  # Увеличиваем количество overflow соединений
    pool_timeout=30,  # Время ожидания соединения
    pool_recycle=3600, # Время перерасхода соединения
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для создания таблиц (вручную или через Alembic)
def init_db():
    Base.metadata.create_all(bind=engine)


# Взаимодействие с базой данных через сессию
def get_db_session():
    return Session()
