from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """
    用户创建模型
    """
    username: str
    password: str
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None


class UserUpdate(UserBase):
    """
    用户更新模型
    """
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """
    数据库中的用户模型
    """
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """
    用户返回模型
    """
    pass


class UserInDB(UserInDBBase):
    """
    数据库中的带密码哈希的用户模型
    """
    hashed_password: str 