from pydantic import BaseModel, Field
from typing import Optional, List


class CityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)


class CityCreate(CityBase):
    pass


class CityResponse(CityBase):
    id: int
    
    class Config:
        from_attributes = True


class CityWithCount(CityResponse):
    services_count: int = 0

