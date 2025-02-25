from sqlalchemy import Column, Integer, String, ForeignKey, Index, Table, Text, DECIMAL, Float, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import TimestampMixin

# Связующая таблица для типов ремонтов и самих ремонтов
repair_type_repair = Table(
    'repair_type_repair',
    Base.metadata,
    Column('repair_id', Integer, ForeignKey('repairs.id'), primary_key=True),
    Column('repair_type_id', Integer, ForeignKey('repair_types.id'), primary_key=True)
)


class Repair(Base, TimestampMixin):
    __tablename__ = 'repairs'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Связь с RepairType через связующую таблицу
    repair_types = relationship('RepairType', secondary=repair_type_repair, back_populates='repairs')
    repair_prices = relationship("RepairPrice", back_populates="repair")

    def __repr__(self):
        return f"<Repair(id={self.id}, name='{self.name}')>"


class RepairType(Base, TimestampMixin):
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
        return f"<RepairType(id={self.id}, name='{self.name}')>"


class ModelRepair(Base, TimestampMixin):
    __tablename__ = 'model_repairs'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('device_models.id'), nullable=False)
    repair_type_id = Column(Integer, ForeignKey('repair_types.id'), nullable=False)
    complexity = Column(String(50), nullable=True)

    # Дополнительные поля
    estimated_time = Column(Integer, nullable=True)  # в минутах

    # Отношения
    model = relationship('DeviceModel', back_populates='repairs')
    repair_type = relationship('RepairType', back_populates='model_repairs')

    def __repr__(self):
        return f"<ModelRepair(id={self.id}, model_id={self.model_id}, repair_type_id={self.repair_type_id})>"


class Part(Base, TimestampMixin):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    retail_price = Column(DECIMAL(precision=10, scale=2), CheckConstraint('retail_price >= 0'), nullable=False)
    currency = Column(String(3), nullable=True, default="RUB")

    # Дополнительные поля
    manufacturer = Column(String(100), nullable=True)
    sku = Column(String(100), nullable=True, unique=True)
    description = Column(Text, nullable=True)

    # Связь с repair_parts
    repair_parts = relationship('RepairPart', back_populates='part')

    def __repr__(self):
        return f"<Part(id={self.id}, name='{self.name}', retail_price={self.retail_price})>"


class RepairPart(Base, TimestampMixin):
    __tablename__ = 'repair_parts'

    id = Column(Integer, primary_key=True)
    repair_type_id = Column(Integer, ForeignKey('repair_types.id'), nullable=False)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), default=1, nullable=False)

    # Связи
    repair_type = relationship('RepairType', back_populates='repair_parts')
    part = relationship('Part', back_populates='repair_parts')

    def __repr__(self):
        return f"<RepairPart(id={self.id}, repair_type_id={self.repair_type_id}, part_id={self.part_id}, quantity={self.quantity})>"


class RepairPrice(Base, TimestampMixin):
    __tablename__ = "repair_prices"

    id = Column(Integer, primary_key=True)
    device_model_id = Column(Integer, ForeignKey('device_models.id'), nullable=False)
    repair_id = Column(Integer, ForeignKey('repairs.id'), nullable=False)
    price = Column(Float, CheckConstraint('price >= 0'), nullable=True)

    # Связи
    device_model = relationship("DeviceModel", back_populates="repair_prices")
    repair = relationship("Repair", back_populates="repair_prices")
    history = relationship("PriceAnalytic", back_populates="repair_price")

    __table_args__ = (
        Index('idx_repair_price_device_model_id', 'device_model_id'),
        Index('idx_repair_price_repair_id', 'repair_id'),
    )

    def __repr__(self):
        return f"<RepairPrice(id={self.id}, repair_id={self.repair_id}, price={self.price})>"


class Price(Base, TimestampMixin):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    repair_price_id = Column(Integer, ForeignKey('repair_prices.id'), nullable=False)
    price = Column(Float, CheckConstraint('price >= 0'), nullable=False)

    # Связи
    service_center = relationship("ServiceCenter", back_populates="prices")
    repair_price = relationship("RepairPrice")

    __table_args__ = (
        Index('idx_price_service_center_id', 'service_center_id'),
        Index('idx_price_repair_price_id', 'repair_price_id'),
    )

    def __repr__(self):
        return f"<Price(id={self.id}, service_center_id={self.service_center_id}, repair_price_id={self.repair_price_id}, price={self.price})>"


class PriceAnalytic(Base, TimestampMixin):
    __tablename__ = "price_analytics"

    id = Column(Integer, primary_key=True)
    repair_price_id = Column(Integer, ForeignKey('repair_prices.id'), nullable=False)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    price = Column(Float, CheckConstraint('price >= 0'), nullable=False)

    # Отношения
    repair_price = relationship("RepairPrice", back_populates="history")
    service_center = relationship("ServiceCenter", back_populates="price_analytics")

    def __repr__(self):
        return f"<PriceAnalytic(id={self.id}, repair_price_id={self.repair_price_id}, price={self.price})>"