from __future__ import annotations

from app.models import AlarmEvent, DeviceStatus, EnvironmentReading


def test_environment_endpoints(client, list_entities):
    payload = {
        "location": "hq",
        "temperature": 24.3,
        "humidity": 48.1,
        "air_quality_index": 37.2,
    }

    response = client.post("/api/environment", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["location"] == "hq"

    listing = client.get("/api/environment", params={"limit": 10})
    assert listing.status_code == 200
    items = listing.json()
    assert len(items) == 1
    assert items[0]["temperature"] == payload["temperature"]

    readings = list_entities(EnvironmentReading)
    assert len(readings) == 1


def test_device_upsert_and_listing(client, list_entities):
    first = {
        "device_id": "gateway-1",
        "name": "Gateway",
        "status": "online",
        "meta": {"ip": "10.0.0.1"},
    }

    second = {
        "device_id": "gateway-1",
        "name": "Gateway",
        "status": "maintenance",
        "meta": {"ip": "10.0.0.1", "firmware": "1.2.0"},
    }

    created = client.post("/api/devices", json=first)
    assert created.status_code == 200

    updated = client.post("/api/devices", json=second)
    assert updated.status_code == 200
    data = updated.json()
    assert data["status"] == "maintenance"
    assert data["meta"]["firmware"] == "1.2.0"

    listing = client.get("/api/devices")
    assert listing.status_code == 200
    entries = listing.json()
    assert len(entries) == 1
    assert entries[0]["status"] == "maintenance"

    devices = list_entities(DeviceStatus)
    assert len(devices) == 1


def test_alarm_creation(client, list_entities):
    payload = {
        "code": "DEVICE_OFFLINE",
        "message": "Sensor offline",
        "severity": "critical",
        "device_id": "sensor-9",
    }

    response = client.post("/api/alarms", json=payload)
    assert response.status_code == 200
    alarm = response.json()
    assert alarm["code"] == "DEVICE_OFFLINE"

    listing = client.get("/api/alarms")
    assert listing.status_code == 200
    alarms = listing.json()
    assert len(alarms) == 1

    stored = list_entities(AlarmEvent)
    assert len(stored) == 1
