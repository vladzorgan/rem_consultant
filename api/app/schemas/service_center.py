from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.models.common import RequestStatus, LinkType


# Базовые схемы для ServiceCenter
class ServiceCenterBase(BaseModel):
    name: str
    city_id: Optional[int] = None
    owner_id: Optional[int] = None
    phone: Optional[str] = None


class ServiceCenterCreate(ServiceCenterBase):
    pass


class ServiceCenterUpdate(ServiceCenterBase):
    name: Optional[str] = None


# Схемы для ServiceCenterAddress
class ServiceCenterAddressBase(BaseModel):
    service_center_id: int
    name: str
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ServiceCenterAddressCreate(ServiceCenterAddressBase):
    pass


class ServiceCenterAddressUpdate(ServiceCenterAddressBase):
    service_center_id: Optional[int] = None
    name: Optional[str] = None


# Схемы для ServiceCenterLink
class ServiceCenterLinkBase(BaseModel):
    service_center_id: int
    type: Optional[LinkType] = None
    link: str


class ServiceCenterLinkCreate(ServiceCenterLinkBase):
    pass


class ServiceCenterLinkUpdate(ServiceCenterLinkBase):
    service_center_id: Optional[int] = None
    link: Optional[str] = None


# Схемы для Review
class ReviewBase(BaseModel):
    service_center_id: int
    author: str
    rating: Optional[float] = Field(None, ge=0, le=5)
    text: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(ReviewBase):
    service_center_id: Optional[int] = None
    author: Optional[str] = None


# Схемы для AddServiceRequest
class AddServiceRequestBase(BaseModel):
    service_center_id: int
    telegram_id: int
    message: str
    contact: str
    status: RequestStatus = RequestStatus.PENDING


class AddServiceRequestCreate(AddServiceRequestBase):
    pass


class AddServiceRequestUpdate(AddServiceRequestBase):
    service_center_id: Optional[int] = None
    telegram_id: Optional[int] = None
    message: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[RequestStatus] = None


# Результирующие схемы
class ServiceCenterAddress(ServiceCenterAddressBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceCenterLink(ServiceCenterLinkBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Review(ReviewBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AddServiceRequest(AddServiceRequestBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceCenter(ServiceCenterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    addresses: List[ServiceCenterAddress] = []
    links: List[ServiceCenterLink] = []
    reviews: List[Review] = []

    class Config:
        from_attributes = True


class ServiceCenterDetail(ServiceCenter):
    city: Optional[Any] = None  # Из схемы location
    owner: Optional[Any] = None  # Из схемы user
    prices: List[Any] = []      # Из схемы repair

    class Config:
        from_attributes = True


# Схемы для пагинации
class ServiceCenterPagination(BaseModel):
    items: List[ServiceCenter]
    total: int
    page: int
    size: int
    pages: int


class ReviewPagination(BaseModel):
    items: List[Review]
    total: int
    page: int
    size: int
    pages: int


class AddServiceRequestPagination(BaseModel):
    items: List[AddServiceRequest]
    total: int
    page: int
    size: int
    pages: int