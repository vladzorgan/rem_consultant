from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, condecimal
from datetime import datetime


# Базовые схемы для Repair
class RepairBase(BaseModel):
    name: str
    description: Optional[str] = None


class RepairCreate(RepairBase):
    pass


class RepairUpdate(RepairBase):
    name: Optional[str] = None


# Базовые схемы для RepairType
class RepairTypeBase(BaseModel):
    group_name: str
    name: str
    description: Optional[str] = None


class RepairTypeCreate(RepairTypeBase):
    pass


class RepairTypeUpdate(RepairTypeBase):
    group_name: Optional[str] = None
    name: Optional[str] = None


# Базовые схемы для Part
class PartBase(BaseModel):
    name: str
    retail_price: condecimal(ge=0, decimal_places=2)
    currency: str = "RUB"
    manufacturer: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None


class PartCreate(PartBase):
    pass


class PartUpdate(PartBase):
    name: Optional[str] = None
    retail_price: Optional[condecimal(ge=0, decimal_places=2)] = None
    currency: Optional[str] = None


# Базовые схемы для RepairPart
class RepairPartBase(BaseModel):
    repair_type_id: int
    part_id: int
    quantity: int = Field(gt=0, default=1)


class RepairPartCreate(RepairPartBase):
    pass


class RepairPartUpdate(RepairPartBase):
    repair_type_id: Optional[int] = None
    part_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)


# Базовые схемы для ModelRepair
class ModelRepairBase(BaseModel):
    model_id: int
    repair_type_id: int
    complexity: Optional[str] = None
    estimated_time: Optional[int] = None  # в минутах


class ModelRepairCreate(ModelRepairBase):
    pass


class ModelRepairUpdate(ModelRepairBase):
    model_id: Optional[int] = None
    repair_type_id: Optional[int] = None


# Базовые схемы для RepairPrice
class RepairPriceBase(BaseModel):
    device_model_id: int
    repair_id: int
    price: Optional[float] = Field(None, ge=0)


class RepairPriceCreate(RepairPriceBase):
    pass


class RepairPriceUpdate(RepairPriceBase):
    device_model_id: Optional[int] = None
    repair_id: Optional[int] = None
    price: Optional[float] = Field(None, ge=0)


# Базовые схемы для ServiceCenterPrice
class PriceBase(BaseModel):
    service_center_id: int
    repair_price_id: int
    price: float = Field(ge=0)


class PriceCreate(PriceBase):
    pass


class PriceUpdate(PriceBase):
    service_center_id: Optional[int] = None
    repair_price_id: Optional[int] = None
    price: Optional[float] = Field(None, ge=0)


# Схемы для результатов
class Part(PartBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RepairPart(RepairPartBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    part: Optional[Part] = None

    class Config:
        from_attributes = True


class RepairType(RepairTypeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    repair_parts: List[RepairPart] = []

    class Config:
        from_attributes = True


class Repair(RepairBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    repair_types: List[RepairType] = []

    class Config:
        from_attributes = True


class ModelRepair(ModelRepairBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    repair_type: Optional[RepairType] = None
    model: Optional[Any] = None  # DeviceModel from device.py

    class Config:
        from_attributes = True


class RepairPrice(RepairPriceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    device_model: Optional[Any] = None  # DeviceModel from device.py
    repair: Optional[Repair] = None

    class Config:
        from_attributes = True


class Price(PriceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    service_center: Optional[Any] = None  # ServiceCenter from service_center.py
    repair_price: Optional[RepairPrice] = None

    class Config:
        from_attributes = True


# Схемы для пагинации
class RepairPagination(BaseModel):
    items: List[Repair]
    total: int
    page: int
    size: int
    pages: int


class RepairTypePagination(BaseModel):
    items: List[RepairType]
    total: int
    page: int
    size: int
    pages: int


class PartPagination(BaseModel):
    items: List[Part]
    total: int
    page: int
    size: int
    pages: int


class ModelRepairPagination(BaseModel):
    items: List[ModelRepair]
    total: int
    page: int
    size: int
    pages: int


class RepairPricePagination(BaseModel):
    items: List[RepairPrice]
    total: int
    page: int
    size: int
    pages: int


class PricePagination(BaseModel):
    items: List[Price]
    total: int
    page: int
    size: int
    pages: int


# Схемы для аналитики
class PriceAnalysis(BaseModel):
    repair_id: int
    repair_name: str
    model_id: int
    model_name: str
    average_price: float
    min_price: float
    max_price: float
    price_count: int
    price_range: Dict[str, int]  # Диапазон цен и количество в каждом диапазоне