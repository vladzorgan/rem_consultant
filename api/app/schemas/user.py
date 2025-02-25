from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    SERVICE_OWNER = "service_owner"
    ADMIN = "admin"


# Базовые схемы для User
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str


# Схема для результатов
class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Схема с токеном для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int  # Unix timestamp
    user: User


# Схема для пагинации пользователей
class UserPagination(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int
    pages: int