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

## Testing

The repository ships with a full testing stack covering the backend, frontend and end-to-end flows. All commands below assume the repository root as the working directory.

### Backend unit & integration tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

These tests exercise the async data ingestion pipeline, API endpoints and the simulation-mode switch using an isolated SQLite database.

### Frontend component tests

```bash
cd frontend
npm install
npm run test:run
```

Vitest together with Testing Library validates component state management, realtime event subscriptions and dashboard wiring.

### End-to-end tests

```bash
cd frontend
npm install
npx playwright install --with-deps
npm run test:e2e
```

Playwright boots the Vite dev server, stubs backend APIs and verifies the dashboard’s critical user journeys including realtime mode transitions.

### Continuous integration

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs linting, backend pytest, frontend unit tests, the production build and Playwright end-to-end checks on every push. The workflow definition can be used as a template for other CI platforms.
=======
# IoT Board Backend

This repository contains the data access layer for an agriculture IoT board. It
uses SQLAlchemy as the ORM, Alembic for migrations, and targets a PostgreSQL
database by default (any SQLAlchemy-compatible database such as MySQL can also
be used).

## Project layout

```
backend/
├── __init__.py
├── alembic/
│   ├── env.py
│   ├── versions/
│   │   └── 20240229_0001_initial.py
│   └── alembic.ini
├── config.py
├── crud.py
├── database.py
├── models.py
├── requirements.txt
└── seed.py
```

## Database models

| Table             | Purpose                                      | Key fields                                                                                          |
| ----------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `fields`          | Basic information about managed plots        | `name`, `location`, `area_hectares`, `soil_type`, `created_at`                                       |
| `crops`           | Crops planted within a field                 | `field_id`, `name`, `variety`, `planting_date`, `growth_stage`, `expected_harvest_date`             |
| `devices`         | IoT hardware installed on a field            | `field_id`, `name`, `device_type`, `manufacturer`, `status`, `installed_at`                         |
| `sensor_readings` | Measurements recorded by devices             | `device_id`, `sensor_type`, `value`, `unit`, `recorded_at`, `notes`                                 |
| `operations`      | Operational log for field/crop maintenance   | `field_id`, `crop_id`, `operation_type`, `description`, `performed_at`, `operator`                  |

Relationships between entities are defined using SQLAlchemy ORM relationships
and exposed through the convenience CRUD helpers in `backend/crud.py`. These
functions are meant to be shared by both the administration backend and large
screen APIs, providing a single source of truth for data access.

## Getting started

### 1. Create a virtual environment & install dependencies

```
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure the database connection

Set the `DATABASE_URL` environment variable to point to your PostgreSQL or
MySQL instance, e.g.

```
export DATABASE_URL=postgresql+psycopg2://iot:iot@localhost:5432/iot_board
```

Optional environment variables:

- `DATABASE_ECHO`: set to `1` to enable SQL logging.

### 3. Run database migrations

Execute Alembic from the repository root so the `backend` package is discoverable
by Python:

The project uses Alembic for schema management. The configuration is located in
`backend/alembic.ini` and uses the database URL from the environment.

```
alembic -c backend/alembic.ini upgrade head
```

To revert:

```
alembic -c backend/alembic.ini downgrade base
```

### 4. Load sample data (optional)

```
python -m backend.seed
```

This script inserts sample fields, crops, devices, sensor readings, and
operations to quickly visualize data in the admin interface or dashboard.

### 5. Using the CRUD helpers

```
from backend.database import session_scope
from backend import crud

with session_scope() as session:
    fields = crud.list_fields(session)
    first_field = crud.get_field(session, fields[0].id)
```

These helpers return ORM objects that can be serialized or further processed by
API layers.

## Development notes

- The ORM models live in `backend/models.py` and can be extended with additional
  fields or relationships as required.
- Keep Alembic migrations in sync when the models change by running
  `alembic revision --autogenerate -m "<message>"`.
- Seed data is intentionally lightweight; adjust the sample payload in
  `backend/seed.py` to match your demo needs.

