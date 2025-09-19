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
