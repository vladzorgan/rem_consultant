# /app/app/schemas/price.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PriceCreateSchema(BaseModel):
    service_center_id: int
    device_brand_id: int
    device_model_id: int
    repair_id: int
    price: float = Field(..., ge=0)  # Цена не может быть отрицательной

class PriceResponseSchema(BaseModel):
    id: int
    service_center_id: int
    device_brand_id: int
    device_model_id: int
    repair_id: int
    price: float
    history: List["PriceHistorySchema"] = []

    class Config:
        from_attributes = True

class PriceHistorySchema(BaseModel):
    id: int
    price_id: int
    old_price: float
    new_price: float
    change_date: datetime

    class Config:
        from_attributes = True