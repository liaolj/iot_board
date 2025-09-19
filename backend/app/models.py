"""Database models for IoT board entities."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class EnvironmentReading(Base):
    """Stores environmental sensor values such as temperature and humidity."""

    __tablename__ = "environment_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location: Mapped[str] = mapped_column(String(64), default="default")
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    air_quality_index: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)


class DeviceStatus(Base):
    """Represents the current state of an IoT device."""

    __tablename__ = "device_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)


class AlarmEvent(Base):
    """High priority alerts that should be surfaced immediately."""

    __tablename__ = "alarm_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(16), default="info")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    device_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class RealTimeDispatchLog(Base):
    """Optional log of broadcasted payloads for auditing."""

    __tablename__ = "realtime_dispatch_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)


__all__ = [
    "EnvironmentReading",
    "DeviceStatus",
    "AlarmEvent",
    "RealTimeDispatchLog",
]
