from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import db as db_module
from app.config import get_settings
from app.db import Base, get_async_session, get_engine
from app.main import create_app


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def configure_test_database(tmp_path, monkeypatch) -> Iterator[None]:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("IOT_BOARD_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("IOT_BOARD_SIMULATION_MODE", "false")
    get_settings.cache_clear()
    db_module._engine = None
    db_module._session_factory = None
    yield
    db_module._engine = None
    db_module._session_factory = None


async def _create_schema() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _drop_schema() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
def prepare_database(configure_test_database) -> Iterator[None]:
    asyncio.run(_create_schema())
    yield
    asyncio.run(_drop_schema())


@pytest.fixture()
def app(prepare_database):
    return create_app()


@pytest.fixture()
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as instance:
        yield instance


@pytest.fixture()
def list_entities() -> Callable[[type], list[object]]:
    async def _list(model: type) -> list[object]:
        async with get_async_session() as session:
            result = await session.execute(select(model))
            return list(result.scalars())

    def wrapper(model: type) -> list[object]:
        return asyncio.run(_list(model))

    return wrapper
