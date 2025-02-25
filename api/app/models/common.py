import enum
from datetime import datetime
from sqlalchemy import Column, DateTime

# Общие перечисления
class RequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DeviceType(enum.Enum):
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    SMARTWATCH = "smartwatch"
    OTHER = "other"

class LinkType(enum.Enum):
    WEBSITE = "website"
    TELEGRAM = "telegram"
    VK = "vk"
    INSTAGRAM = "instagram"
    OTHER = "other"

# Миксин для добавления полей created_at и updated_at
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)