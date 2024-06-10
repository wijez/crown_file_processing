from typing import Optional

from pydantic import BaseModel, EmailStr


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
    verify_code: Optional[str]


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserSchema(UserBase):
    id: int



