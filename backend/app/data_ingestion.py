"""Data ingestion utilities for pushing IoT updates into the system."""

from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import Awaitable, Callable

from sqlalchemy import select

from .config import get_settings
from .db import get_async_session
from .models import AlarmEvent, DeviceStatus, EnvironmentReading, RealTimeDispatchLog
from .realtime import manager
from .schemas import BroadcastEnvelope


async def upsert_device_status(
    device_id: str, name: str, status: str, meta: dict | None = None
) -> DeviceStatus:
    meta = meta or {}
    async with get_async_session() as session:
        stmt = select(DeviceStatus).where(DeviceStatus.device_id == device_id)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            instance = DeviceStatus(device_id=device_id, name=name, status=status, meta=meta)
            session.add(instance)
        else:
            instance.status = status
            instance.meta = meta
        instance.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(instance)
    return instance


async def create_environment_reading(**kwargs) -> EnvironmentReading:
    async with get_async_session() as session:
        reading = EnvironmentReading(**kwargs)
        session.add(reading)
        await session.commit()
        await session.refresh(reading)
    return reading


async def create_alarm_event(**kwargs) -> AlarmEvent:
    async with get_async_session() as session:
        alarm = AlarmEvent(**kwargs)
        session.add(alarm)
        await session.commit()
        await session.refresh(alarm)
    return alarm


async def persist_and_broadcast(event: str, payload: dict) -> None:
    envelope = BroadcastEnvelope(event=event, payload=payload)
    async with get_async_session() as session:
        session.add(RealTimeDispatchLog(event_type=event, payload=payload))
        await session.commit()
    await manager.broadcast(envelope)


async def handle_environment_update(data: dict) -> None:
    reading = await create_environment_reading(**data)
    await persist_and_broadcast(
        "environment.update",
        {
            "id": reading.id,
            "location": reading.location,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "air_quality_index": reading.air_quality_index,
            "created_at": reading.created_at.isoformat(),
        },
    )


async def handle_device_status(data: dict) -> None:
    status = await upsert_device_status(**data)
    await persist_and_broadcast(
        "device.update",
        {
            "id": status.id,
            "device_id": status.device_id,
            "name": status.name,
            "status": status.status,
            "meta": status.meta,
            "updated_at": status.updated_at.isoformat(),
        },
    )


async def handle_alarm(data: dict) -> None:
    alarm = await create_alarm_event(**data)
    await persist_and_broadcast(
        "alarm.raise",
        {
            "id": alarm.id,
            "code": alarm.code,
            "message": alarm.message,
            "severity": alarm.severity,
            "device_id": alarm.device_id,
            "created_at": alarm.created_at.isoformat(),
        },
    )


async def simulation_worker(stop_event: asyncio.Event) -> None:
    """Periodically generate demo payloads when simulation mode is enabled."""

    settings = get_settings()
    interval = settings.simulation_interval_seconds
    counter = 0
    while not stop_event.is_set():
        await asyncio.sleep(interval)
        counter += 1
        temperature = round(20 + random.random() * 5, 2)
        humidity = round(40 + random.random() * 20, 2)
        aqi = round(50 + random.random() * 20, 2)
        await handle_environment_update(
            {
                "location": "demo",
                "temperature": temperature,
                "humidity": humidity,
                "air_quality_index": aqi,
            }
        )
        status = random.choice(["online", "offline", "maintenance"])
        await handle_device_status(
            {
                "device_id": "demo-device",
                "name": "Demo Sensor",
                "status": status,
                "meta": {"iteration": counter},
            }
        )
        if status == "offline":
            await handle_alarm(
                {
                    "code": "DEVICE_OFFLINE",
                    "message": "Demo sensor lost connectivity",
                    "severity": "warning",
                    "device_id": "demo-device",
                }
            )


async def start_background_tasks() -> Callable[[], Awaitable[None]]:
    """Launch data listeners and return a shutdown callback."""

    settings = get_settings()
    stop_event = asyncio.Event()
    tasks = []

    if settings.simulation_mode:
        tasks.append(asyncio.create_task(simulation_worker(stop_event)))

    async def shutdown() -> None:
        stop_event.set()
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass

    return shutdown


__all__ = [
    "handle_environment_update",
    "handle_device_status",
    "handle_alarm",
    "start_background_tasks",
]
