from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session
from typing import Generator, AsyncGenerator
from app.core.config import get_settings

settings = get_settings()

# Synchronous database setup
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous database setup
async_engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
