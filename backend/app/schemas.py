"""Pydantic schemas for API payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class EnvironmentReadingIn(BaseModel):
    location: str = Field(default="default")
    temperature: float
    humidity: float
    air_quality_index: float = Field(alias="aqi")

    class Config:
        populate_by_name = True


class EnvironmentReadingOut(EnvironmentReadingIn):
    id: int
    created_at: datetime


class DeviceStatusIn(BaseModel):
    device_id: str
    name: str
    status: Literal["online", "offline", "maintenance", "error", "warning"]
    meta: dict[str, Any] = Field(default_factory=dict)


class DeviceStatusOut(DeviceStatusIn):
    id: int
    updated_at: datetime


class AlarmEventIn(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "critical"]
    device_id: str | None = None


class AlarmEventOut(AlarmEventIn):
    id: int
    created_at: datetime


class BroadcastEnvelope(BaseModel):
    """Common structure used for data pushed to realtime channels."""

    event: str
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = [
    "EnvironmentReadingIn",
    "EnvironmentReadingOut",
    "DeviceStatusIn",
    "DeviceStatusOut",
    "AlarmEventIn",
    "AlarmEventOut",
    "BroadcastEnvelope",
]
