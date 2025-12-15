from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(UserBase):
    id: int
    balance: Decimal = Decimal("0")
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BalanceOperation(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Сумма операции (должна быть положительной)")


class BalanceResponse(BaseModel):
    balance: Decimal
    message: str

