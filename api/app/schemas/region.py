# /app/app/schemas/region.py
from pydantic import BaseModel

class RegionSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy