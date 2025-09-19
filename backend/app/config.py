"""Configuration helpers for the IoT Board backend."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    database_url: str = Field(
        default="sqlite+aiosqlite:///./iot_board.db",
        description="SQLAlchemy compatible database URL.",
    )
    simulation_mode: bool = Field(
        default=True,
        description="Enable synthetic data generation for demos and tests.",
    )
    simulation_interval_seconds: float = Field(
        default=2.0,
        description="Interval for pushing synthetic data when simulation mode is enabled.",
    )
    realtime_channel: Literal["websocket", "sse"] = Field(
        default="websocket",
        description="Preferred realtime push channel type.",
    )

    class Config:
        env_prefix = "IOT_BOARD_"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
