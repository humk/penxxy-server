from typing import Optional
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class User(Base):
    """
    用户模型
    """
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    mobile = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # 微信相关
    openid = Column(String(50), unique=True, index=True, nullable=True)
    unionid = Column(String(50), unique=True, index=True, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int) -> Optional["User"]:
        """
        通过ID获取用户
        """
        result = await db.execute(select(cls).filter(cls.id == id))
        return result.scalars().first()
    
    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str) -> Optional["User"]:
        """
        通过用户名获取用户
        """
        result = await db.execute(select(cls).filter(cls.username == username))
        return result.scalars().first()
    
    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> Optional["User"]:
        """
        通过邮箱获取用户
        """
        result = await db.execute(select(cls).filter(cls.email == email))
        return result.scalars().first()
    
    @classmethod
    async def get_by_openid(cls, db: AsyncSession, openid: str) -> Optional["User"]:
        """
        通过微信OpenID获取用户
        """
        result = await db.execute(select(cls).filter(cls.openid == openid))
        return result.scalars().first() 