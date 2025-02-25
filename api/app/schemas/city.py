# /app/app/schemas/city.py
from pydantic import BaseModel

class CitySchema(BaseModel):
    id: int
    name: str
    region_id: int
    population: int

    class Config:
        from_attributes = True