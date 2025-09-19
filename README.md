# IoT Board

This repository contains a demo IoT command center with a FastAPI backend and a React dashboard. The backend exposes REST, WebSocket and Server-Sent Event (SSE) interfaces that push real-time updates to the dashboard. A simulation mode periodically generates environmental readings, device status changes and alarm events so the entire stack can be demonstrated without connecting to real devices.

## Backend

The backend lives in [`backend/`](backend/) and is built with FastAPI. It exposes REST endpoints under `/api` for querying recent data and provides a WebSocket endpoint at `/api/ws` plus an SSE stream at `/api/events`. A background scheduler ingests incoming payloads, persists them to SQLite and broadcasts the events to connected clients.

### Running the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables prefixed with `IOT_BOARD_` can be used to override configuration, for example `IOT_BOARD_SIMULATION_MODE=false` to disable the synthetic data generator.

## Frontend

The frontend lives in [`frontend/`](frontend/) and is a small Vite + React project. It uses a dedicated realtime service (`src/services/realtime.ts`) that handles WebSocket lifecycles, automatic reconnection and SSE fallback. Dashboard widgets subscribe to relevant events and refresh themselves instantly when new payloads arrive.

### Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies API calls to `http://localhost:8000` by default.

## Development notes

* When the backend starts, a simulation worker pushes demo data every few seconds. This keeps the dashboard lively in demos.
* The backend uses SQLite via SQLAlchemy's async engine. Database schema is created automatically on startup.
* Realtime broadcasts are logged in the `realtime_dispatch_log` table for traceability.
