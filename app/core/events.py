import logging
from typing import Callable
from fastapi import FastAPI

from app.db.session import engine
from app.db.base import Base
from app.utils.logger import get_logger

logger = get_logger("db")


def startup_event_handler(app: FastAPI) -> Callable:
    """
    应用程序启动事件处理
    """
    async def startup() -> None:
        # 创建数据库表
        try:
            async with engine.begin() as conn:
                # 仅在开发环境下自动创建表，生产环境应使用迁移工具
                from app.core.config import settings
                if settings.DEBUG:
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
        
        get_logger("app").info("应用程序启动完成")
    
    return startup


def shutdown_event_handler(app: FastAPI) -> Callable:
    """
    应用程序关闭事件处理
    """
    async def shutdown() -> None:
        get_logger("app").info("应用程序关闭")
    
    return shutdown