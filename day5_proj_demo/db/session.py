from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.settings import settings
from typing import AsyncGenerator

def get_async_engine():
    db_url = settings.DATABASE_URL
    # 关键：异步连接串前缀要改！
    # sqlite 同步: sqlite:///xxx.db
    # sqlite 异步: sqlite+aiosqlite:///xxx.db
    # postgres同步: postgresql://
    # postgres异步: postgresql+asyncpg://
    if db_url.startswith("sqlite"):
        if not db_url.startswith("sqlite+aiosqlite"):
            # 自动替换为异步协议
            db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        engine = create_async_engine(
            db_url,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return engine

engine = get_async_engine()
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # 异步非常重要！提交后对象不失效，可以继续读取属性
)

# 异步依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
