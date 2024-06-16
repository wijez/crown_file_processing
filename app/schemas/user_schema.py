from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.users_model import UserRole


class UserBase(BaseModel):
    full_name: str
    username: str
    password: str
    email: EmailStr


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserVerifyCodeSchema(BaseModel):
    email: EmailStr
    verify_code: str


class UserCreateSchema(UserBase):
    role: Optional[UserRole]
    verify_code: Optional[str]


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserSchema(UserBase):
    id: UUID




