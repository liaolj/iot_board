"""API routes for IoT board backend."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from .data_ingestion import (
    handle_alarm,
    handle_device_status,
    handle_environment_update,
)
from .db import get_async_session
from .models import AlarmEvent, DeviceStatus, EnvironmentReading
from .realtime import manager, sse_endpoint
from .schemas import (
    AlarmEventIn,
    AlarmEventOut,
    DeviceStatusIn,
    DeviceStatusOut,
    EnvironmentReadingIn,
    EnvironmentReadingOut,
)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.register_websocket(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.unregister_websocket(websocket)


@router.get("/events")
async def events_stream():
    return await sse_endpoint()


@router.post("/environment", response_model=EnvironmentReadingOut)
async def post_environment_reading(payload: EnvironmentReadingIn):
    await handle_environment_update(payload.model_dump())
    async with get_async_session() as session:
        stmt = select(EnvironmentReading).order_by(EnvironmentReading.id.desc())
        result = await session.execute(stmt)
        return result.scalars().first()


@router.get("/environment", response_model=list[EnvironmentReadingOut])
async def list_environment_readings(limit: int = 20):
    async with get_async_session() as session:
        stmt = select(EnvironmentReading).order_by(EnvironmentReading.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())


@router.post("/devices", response_model=DeviceStatusOut)
async def post_device_status(payload: DeviceStatusIn):
    await handle_device_status(payload.model_dump())
    async with get_async_session() as session:
        stmt = select(DeviceStatus).where(DeviceStatus.device_id == payload.device_id)
        result = await session.execute(stmt)
        return result.scalar_one()


@router.get("/devices", response_model=list[DeviceStatusOut])
async def list_devices():
    async with get_async_session() as session:
        stmt = select(DeviceStatus)
        result = await session.execute(stmt)
        return list(result.scalars())


@router.post("/alarms", response_model=AlarmEventOut)
async def post_alarm(payload: AlarmEventIn):
    await handle_alarm(payload.model_dump())
    async with get_async_session() as session:
        stmt = select(AlarmEvent).order_by(AlarmEvent.id.desc())
        result = await session.execute(stmt)
        return result.scalars().first()


@router.get("/alarms", response_model=list[AlarmEventOut])
async def list_alarms(limit: int = 20):
    async with get_async_session() as session:
        stmt = select(AlarmEvent).order_by(AlarmEvent.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())


__all__ = ["router"]
