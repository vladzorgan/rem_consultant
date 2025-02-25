from sqlalchemy import Column, Integer, String, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import TimestampMixin, DeviceType


class DeviceBrand(Base, TimestampMixin):
    __tablename__ = "device_brands"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)

    # Отношения
    models = relationship("DeviceModel", back_populates="brand", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DeviceBrand(id={self.id}, name='{self.name}')>"


class DeviceModel(Base, TimestampMixin):
    __tablename__ = "device_models"

    id = Column(Integer, primary_key=True)
    device_brand_id = Column(Integer, ForeignKey('device_brands.id'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    # Дополнительные поля для расширения функционала
    release_year = Column(Integer, nullable=True)
    display_size = Column(String, nullable=True)
    processor = Column(String, nullable=True)
    ram = Column(String, nullable=True)
    storage = Column(String, nullable=True)

    # Отношения
    brand = relationship("DeviceBrand", back_populates="models")
    repairs = relationship("ModelRepair", back_populates="model", cascade="all, delete-orphan")
    repair_prices = relationship("RepairPrice", back_populates="device_model")

    __table_args__ = (
        Index('idx_device_model_brand_id', 'device_brand_id'),
        Index('idx_device_model_type', 'type'),
    )

    def __repr__(self):
        return f"<DeviceModel(id={self.id}, name='{self.name}', brand_id={self.device_brand_id})>"

    @property
    def full_name(self):
        """Возвращает полное имя модели с брендом"""
        if hasattr(self, 'brand') and self.brand:
            return f"{self.brand.name} {self.name}"
        return self.name