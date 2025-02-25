from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, nullable=True)

    # Дополнительные поля для расширения функциональности
    is_admin = Column(Boolean, default=False, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)

    # Отношения
    city = relationship("City", back_populates="users")
    service_centers = relationship("ServiceCenter", back_populates="owner")
    service_claim_requests = relationship("AddServiceRequest", back_populates="user")

    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"

    @property
    def full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return f"User {self.telegram_id}"