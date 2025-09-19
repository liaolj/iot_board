"""Realtime channel manager supporting WebSocket and SSE clients."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Dict, Iterable

from fastapi import WebSocket
from fastapi.responses import EventSourceResponse

from .schemas import BroadcastEnvelope

class RealtimeChannelManager:
    """Keeps track of active realtime connections and pushes broadcast events."""

    def __init__(self) -> None:
        self._websockets: set[WebSocket] = set()
        self._sse_queues: Dict[int, asyncio.Queue[str]] = {}
        self._lock = asyncio.Lock()

    async def register_websocket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._websockets.add(websocket)

    async def unregister_websocket(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._websockets.discard(websocket)

    async def register_sse(self) -> AsyncIterator[Iterable[str]]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        ident = id(queue)
        async with self._lock:
            self._sse_queues[ident] = queue

        try:
            while True:
                payload = await queue.get()
                yield payload
        finally:
            async with self._lock:
                self._sse_queues.pop(ident, None)

    async def broadcast(self, envelope: BroadcastEnvelope) -> None:
        data = envelope.model_dump()
        payload = json.dumps(data, default=str)
        async with self._lock:
            websockets = list(self._websockets)
            queues = list(self._sse_queues.values())

        coroutines = [ws.send_text(payload) for ws in websockets]
        if coroutines:
            await asyncio.gather(*coroutines, return_exceptions=True)

        for queue in queues:
            await queue.put(f"data: {payload}\n\n")

    async def emit(self, event: str, payload: dict) -> None:
        envelope = BroadcastEnvelope(event=event, payload=payload)
        await self.broadcast(envelope)


manager = RealtimeChannelManager()


async def sse_endpoint() -> EventSourceResponse:
    async def event_publisher():
        async for payload in manager.register_sse():
            yield payload

    return EventSourceResponse(event_publisher())


__all__ = ["RealtimeChannelManager", "manager", "sse_endpoint"]
