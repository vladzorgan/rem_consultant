from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Импортируем перечисления из моделей
from app.models.common import DeviceType

# Базовые схемы для DeviceBrand
class DeviceBrandBase(BaseModel):
    name: str


class DeviceBrandCreate(DeviceBrandBase):
    pass


class DeviceBrandUpdate(DeviceBrandBase):
    name: Optional[str] = None


# Базовые схемы для DeviceModel
class DeviceModelBase(BaseModel):
    name: str
    device_brand_id: int
    type: DeviceType = DeviceType.SMARTPHONE
    release_year: Optional[int] = None
    display_size: Optional[str] = None
    processor: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None


class DeviceModelCreate(DeviceModelBase):
    pass


class DeviceModelUpdate(DeviceModelBase):
    name: Optional[str] = None
    device_brand_id: Optional[int] = None
    type: Optional[DeviceType] = None


# Схемы для результатов
class DeviceBrand(DeviceBrandBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceBrandWithModels(DeviceBrand):
    models: List["DeviceModel"] = []


class DeviceModel(DeviceModelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    brand: Optional[DeviceBrand] = None

    class Config:
        from_attributes = True


# Схемы для пагинации
class DeviceBrandPagination(BaseModel):
    items: List[DeviceBrand]
    total: int
    page: int
    size: int
    pages: int


class DeviceModelPagination(BaseModel):
    items: List[DeviceModel]
    total: int
    page: int
    size: int
    pages: int


# Обновляем прямые ссылки для обеспечения правильной типизации
DeviceBrandWithModels.model_rebuild()