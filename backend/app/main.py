"""FastAPI application entrypoint for the IoT board backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .data_ingestion import start_background_tasks
from .db import Base, get_engine
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    shutdown_callback = await start_background_tasks()
    try:
        yield
    finally:
        await shutdown_callback()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="IoT Board Backend", lifespan=lifespan)
    app.include_router(router, prefix="/api")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.settings = settings
    return app


app = create_app()


__all__ = ["create_app", "app"]
