from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Базовые схемы для Region
class RegionBase(BaseModel):
    name: str


class RegionCreate(RegionBase):
    pass


class RegionUpdate(RegionBase):
    name: Optional[str] = None


# Базовые схемы для City
class CityBase(BaseModel):
    name: str
    region_id: int
    population: Optional[int] = 0


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    name: Optional[str] = None
    region_id: Optional[int] = None
    population: Optional[int] = None


# Схемы для результатов
class City(CityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Region(RegionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RegionWithCities(Region):
    cities: List[City] = []


# Схемы для пагинации
class RegionPagination(BaseModel):
    items: List[Region]
    total: int
    page: int
    size: int
    pages: int


class CityPagination(BaseModel):
    items: List[City]
    total: int
    page: int
    size: int
    pages: int