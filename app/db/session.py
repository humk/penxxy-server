from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建异步引擎
# 对SQLite使用aiosqlite驱动
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///"),
        echo=settings.DEBUG,
        future=True,
    )
else:
    # 对PostgreSQL使用asyncpg驱动
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") if settings.DATABASE_URL.startswith("postgresql://") else settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    获取数据库会话依赖
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 