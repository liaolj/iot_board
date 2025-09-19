"""Database utilities for the IoT board backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    """Declarative base class for ORM models."""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return a lazily initialised async engine."""

    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(settings.database_url, echo=False)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared async session factory."""

    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Provide a transactional scope around a series of operations."""

    factory = get_session_factory()
    async with factory() as session:
        yield session


async def run_in_session(callback: Callable[[AsyncSession], AsyncIterator[None] | None]) -> None:
    """Helper to run an async callback within a session, committing afterwards."""

    async with get_async_session() as session:
        try:
            result = callback(session)
            if result is not None and hasattr(result, "__aiter__"):
                async for _ in result:  # pragma: no cover - convenience for async generators
                    pass
            await session.commit()
        except Exception:
            await session.rollback()
            raise


__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_async_session",
    "run_in_session",
]
