"""Seed script to populate the database with sample data."""

from __future__ import annotations

from datetime import datetime, timedelta

from .database import session_scope
from . import crud


SAMPLE_DATA = {
    "fields": [
        {
            "name": "North Field",
            "location": "POINT(120.15 30.28)",
            "area_hectares": 5.5,
            "soil_type": "Loam",
        },
        {
            "name": "South Field",
            "location": "POINT(120.16 30.27)",
            "area_hectares": 3.2,
            "soil_type": "Clay",
        },
    ],
    "crops": [
        {
            "field_index": 0,
            "name": "Rice",
            "variety": "Japonica",
            "planting_date": datetime.utcnow() - timedelta(days=60),
            "growth_stage": "Vegetative",
        },
        {
            "field_index": 1,
            "name": "Corn",
            "variety": "Sweet",
            "planting_date": datetime.utcnow() - timedelta(days=30),
            "growth_stage": "Seedling",
        },
    ],
    "devices": [
        {
            "field_index": 0,
            "name": "Weather Station",
            "device_type": "weather",
            "manufacturer": "Acme",
            "status": "active",
        },
        {
            "field_index": 1,
            "name": "Soil Probe",
            "device_type": "soil",
            "manufacturer": "GreenTech",
            "status": "active",
        },
    ],
}


def seed() -> None:
    """Insert sample data for quick demos."""

    with session_scope() as session:
        fields = [crud.create_field(session, **field) for field in SAMPLE_DATA["fields"]]

        crops = []
        for crop in SAMPLE_DATA["crops"]:
            payload = crop.copy()
            field_index = payload.pop("field_index")
            payload["field_id"] = fields[field_index].id
            crops.append(crud.create_crop(session, **payload))

        devices = []
        for device in SAMPLE_DATA["devices"]:
            payload = device.copy()
            field_index = payload.pop("field_index")
            payload["field_id"] = fields[field_index].id
            devices.append(crud.create_device(session, **payload))

        if devices:
            crud.create_sensor_reading(
                session,
                device_id=devices[0].id,
                sensor_type="temperature",
                value=24.5,
                unit="°C",
            )

        if fields and crops:
            crud.create_operation(
                session,
                field_id=fields[0].id,
                crop_id=crops[0].id,
                operation_type="Fertilization",
                description="Applied nitrogen fertilizer",
            )


if __name__ == "__main__":
    seed()
