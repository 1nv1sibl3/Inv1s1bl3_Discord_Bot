import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import settings
from src.database.models import Base

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        db_url = settings.database_url

        # Ensure sqlite parent directory exists if using local sqlite file
        if db_url.startswith("sqlite"):
            # parse sqlite file path
            prefix = "sqlite+aiosqlite:///"
            if db_url.startswith(prefix):
                sqlite_path = db_url[len(prefix):]
                if not sqlite_path.startswith(":memory:"):
                    db_file = Path(sqlite_path)
                    if not db_file.is_absolute():
                        root_dir = Path(__file__).resolve().parent.parent.parent
                        db_file = root_dir / sqlite_path
                    db_file.parent.mkdir(parents=True, exist_ok=True)
                    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"

        _engine = create_async_engine(
            db_url,
            echo=settings.is_development and settings.log_level == "DEBUG",
            future=True,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async transactional database session context."""
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database tables for the application."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close active database engine pool."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None
