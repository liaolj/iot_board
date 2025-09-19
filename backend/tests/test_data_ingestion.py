from __future__ import annotations

import asyncio

from app import data_ingestion
from app.models import DeviceStatus, EnvironmentReading, RealTimeDispatchLog
from app.realtime import manager
from app.schemas import BroadcastEnvelope


def test_handle_environment_update_persists_and_broadcasts(list_entities, monkeypatch):
    captured: list[BroadcastEnvelope] = []

    async def fake_broadcast(envelope: BroadcastEnvelope) -> None:
        captured.append(envelope)

    monkeypatch.setattr(manager, "broadcast", fake_broadcast)

    payload = {
        "location": "lab",
        "temperature": 21.5,
        "humidity": 55.2,
        "air_quality_index": 42.0,
    }

    asyncio.run(data_ingestion.handle_environment_update(payload))

    readings = list_entities(EnvironmentReading)
    logs = list_entities(RealTimeDispatchLog)

    assert len(readings) == 1
    assert readings[0].location == "lab"
    assert len(logs) == 1
    assert logs[0].event_type == "environment.update"
    assert captured and captured[0].event == "environment.update"


def test_handle_device_status_upserts_and_broadcasts(list_entities, monkeypatch):
    captured: list[BroadcastEnvelope] = []

    async def fake_broadcast(envelope: BroadcastEnvelope) -> None:
        captured.append(envelope)

    monkeypatch.setattr(manager, "broadcast", fake_broadcast)

    first = {
        "device_id": "sensor-1",
        "name": "Sensor",
        "status": "online",
        "meta": {"battery": 95},
    }

    second = {
        "device_id": "sensor-1",
        "name": "Sensor",
        "status": "offline",
        "meta": {"battery": 10},
    }

    asyncio.run(data_ingestion.handle_device_status(first))
    asyncio.run(data_ingestion.handle_device_status(second))

    devices = list_entities(DeviceStatus)
    logs = list_entities(RealTimeDispatchLog)

    assert len(devices) == 1
    assert devices[0].status == "offline"
    assert devices[0].meta == {"battery": 10}
    assert len(logs) == 2
    assert captured[-1].event == "device.update"


def test_start_background_tasks_respects_simulation_mode(monkeypatch):
    monkeypatch.setenv("IOT_BOARD_SIMULATION_MODE", "false")
    data_ingestion.get_settings.cache_clear()

    def forbidden_create_task(_coro):
        raise AssertionError("Simulation worker should not start when disabled")

    monkeypatch.setattr(asyncio, "create_task", forbidden_create_task)

    async def runner() -> None:
        shutdown = await data_ingestion.start_background_tasks()
        await shutdown()

    asyncio.run(runner())


def test_start_background_tasks_launches_simulation(monkeypatch):
    monkeypatch.setenv("IOT_BOARD_SIMULATION_MODE", "true")
    data_ingestion.get_settings.cache_clear()

    started = asyncio.Event()

    async def fake_worker(stop_event: asyncio.Event) -> None:
        started.set()
        await stop_event.wait()

    monkeypatch.setattr(data_ingestion, "simulation_worker", fake_worker)

    created_tasks: list[asyncio.Task[None]] = []
    original_create_task = asyncio.create_task

    def tracking_create_task(coro):
        task = original_create_task(coro)
        created_tasks.append(task)
        return task

    monkeypatch.setattr(asyncio, "create_task", tracking_create_task)

    async def runner() -> None:
        shutdown = await data_ingestion.start_background_tasks()
        await asyncio.wait_for(started.wait(), timeout=1)
        await shutdown()

    asyncio.run(runner())

    assert len(created_tasks) == 1
    assert all(task.cancelled() or task.done() for task in created_tasks)
