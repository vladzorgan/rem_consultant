# /app/app/schemas/review.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreateSchema(BaseModel):
    service_center_id: int
    rating: Optional[float] = Field(None, ge=0, le=5)  # Валидация рейтинга 0-5
    author: str
    text: str

class ReviewResponseSchema(BaseModel):
    id: int
    service_center_id: int
    rating: Optional[float]
    author: str
    text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True