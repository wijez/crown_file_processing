import enum
from sqlalchemy import Column, String, Boolean, Integer, Enum as SQLEnum

from app.models.base_model import BaseModel


class UserRole(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    FRESHER = "FRESHER"
    MEMBER = "MEMBER"


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(65), unique=True, nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(65), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=False, server_default="false", nullable=False)
    verify_code = Column(String(6), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)

