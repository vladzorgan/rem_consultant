from sqlalchemy import Column, Integer, String, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import TimestampMixin


class Region(Base, TimestampMixin):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    # Отношения
    cities = relationship("City", back_populates="region", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_region_name', 'name'),
    )

    def __repr__(self):
        return f"<Region(id={self.id}, name='{self.name}')>"


class City(Base, TimestampMixin):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    population = Column(Integer, default=0, nullable=False)

    # Добавим валидацию данных
    population = Column(
        Integer,
        CheckConstraint('population >= 0'),
        default=0,
        nullable=False
    )

    # Отношения
    region = relationship("Region", back_populates="cities")
    users = relationship("User", back_populates="city")
    service_centers = relationship("ServiceCenter", back_populates="city")

    __table_args__ = (
        Index('idx_city_region_id', 'region_id'),
    )

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}', region_id={self.region_id})>"