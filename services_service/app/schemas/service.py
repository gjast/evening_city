from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class ServiceType(str, Enum):
    WORK = "work"
    ESTATE = "estate"
    NEWS = "news"
    AUTO = "auto"


class ServiceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    service_type: ServiceType


class ServiceCreate(ServiceBase):
    city_id: int


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None


class ServiceResponse(ServiceBase):
    id: int
    city_id: int
    rating: Decimal = Decimal("0")
    reviews_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ServiceWithCity(ServiceResponse):
    city_name: str
    city_slug: str

