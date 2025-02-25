from sqlalchemy import Column, Integer, String, ForeignKey, Index, Enum, Float, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import TimestampMixin, RequestStatus, LinkType


class ServiceCenter(Base, TimestampMixin):
    __tablename__ = "service_centers"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    # Отношения
    city = relationship("City", back_populates="service_centers")
    owner = relationship("User", back_populates="service_centers")
    addresses = relationship("ServiceCenterAddress", back_populates="service_center", cascade="all, delete-orphan")
    links = relationship("ServiceCenterLink", back_populates="service_center", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="service_center", cascade="all, delete-orphan")
    prices = relationship("Price", back_populates="service_center", cascade="all, delete-orphan")
    price_analytics = relationship("PriceAnalytic", back_populates="service_center")

    __table_args__ = (
        Index('idx_service_center_city_id', 'city_id'),
        Index('idx_service_center_owner_id', 'owner_id'),
    )

    def __repr__(self):
        return f"<ServiceCenter(id={self.id}, name='{self.name}')>"


class AddServiceRequest(Base, TimestampMixin):
    __tablename__ = "service_claim_requests"

    id = Column(Integer, primary_key=True, index=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    message = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    status = Column(String, nullable=False)

    # Отношения
    service_center = relationship("ServiceCenter")
    user = relationship("User", back_populates="service_claim_requests")

    __table_args__ = (
        Index('idx_service_claim_service_center_id', 'service_center_id'),
        Index('idx_service_claim_telegram_id', 'telegram_id'),
    )

    def __repr__(self):
        return f"<AddServiceRequest(id={self.id}, status='{self.status.value}')>"


class ServiceCenterAddress(Base, TimestampMixin):
    __tablename__ = "service_center_addresses"

    id = Column(Integer, primary_key=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    name = Column(String, nullable=False)

    # Дополнительные поля для адреса
    street = Column(String, nullable=True)
    building = Column(String, nullable=True)
    apartment = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)

    # Координаты для отображения на карте
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Отношения
    service_center = relationship("ServiceCenter", back_populates="addresses")

    def __repr__(self):
        return f"<ServiceCenterAddress(id={self.id}, name='{self.name}')>"


class ServiceCenterLink(Base, TimestampMixin):
    __tablename__ = "service_center_links"

    id = Column(Integer, primary_key=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    type = Column(String, nullable=True)
    link = Column(String, nullable=False)

    # Отношения
    service_center = relationship("ServiceCenter", back_populates="links")

    def __repr__(self):
        return f"<ServiceCenterLink(id={self.id}, type='{self.type.value if self.type else None}')>"


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    service_center_id = Column(Integer, ForeignKey('service_centers.id'), nullable=False)
    author = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    text = Column(Text, nullable=True)

    # Отношения
    service_center = relationship("ServiceCenter", back_populates="reviews")

    __table_args__ = (
        Index('idx_review_service_center_id', 'service_center_id'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating})>"