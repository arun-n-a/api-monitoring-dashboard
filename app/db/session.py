from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, 
    async_sessionmaker)

from app.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True, # You can also use settings.DEBUG here
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE_IN_SECONDS,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT_IN_SECONDS,
    connect_args={"timeout": settings.DATABASE_CONNECT_TIMEOUT},
    pool_pre_ping=True
    )
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
