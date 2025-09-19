"""CRUD helpers for interacting with the ORM models."""

from __future__ import annotations

from typing import Any, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

ModelType = TypeVar("ModelType", bound=models.Base)


def list_entities(session: Session, model: type[ModelType]) -> Sequence[ModelType]:
    """Return all rows for the given model."""

    statement = select(model)
    return session.scalars(statement).all()


def get_entity(session: Session, model: type[ModelType], entity_id: Any) -> ModelType | None:
    """Return a single entity by primary key or ``None`` if it does not exist."""

    return session.get(model, entity_id)


def create_entity(session: Session, instance: ModelType) -> ModelType:
    """Persist a new instance and return it."""

    session.add(instance)
    session.flush()
    return instance


def update_entity(session: Session, instance: ModelType, data: dict[str, Any]) -> ModelType:
    """Apply ``data`` to ``instance`` and return the updated entity."""

    for key, value in data.items():
        setattr(instance, key, value)
    session.flush()
    return instance


def delete_entity(session: Session, instance: ModelType) -> None:
    """Delete an instance."""

    session.delete(instance)
    session.flush()


# Convenience wrappers -----------------------------------------------------

def create_field(session: Session, **kwargs: Any) -> models.Field:
    return create_entity(session, models.Field(**kwargs))


def create_crop(session: Session, **kwargs: Any) -> models.Crop:
    return create_entity(session, models.Crop(**kwargs))


def create_device(session: Session, **kwargs: Any) -> models.Device:
    return create_entity(session, models.Device(**kwargs))


def create_sensor_reading(session: Session, **kwargs: Any) -> models.SensorReading:
    return create_entity(session, models.SensorReading(**kwargs))


def create_operation(session: Session, **kwargs: Any) -> models.Operation:
    return create_entity(session, models.Operation(**kwargs))


def list_fields(session: Session) -> Sequence[models.Field]:
    return list_entities(session, models.Field)


def list_crops(session: Session) -> Sequence[models.Crop]:
    return list_entities(session, models.Crop)


def list_devices(session: Session) -> Sequence[models.Device]:
    return list_entities(session, models.Device)


def list_sensor_readings(session: Session) -> Sequence[models.SensorReading]:
    return list_entities(session, models.SensorReading)


def list_operations(session: Session) -> Sequence[models.Operation]:
    return list_entities(session, models.Operation)


def get_field(session: Session, entity_id: Any) -> models.Field | None:
    return get_entity(session, models.Field, entity_id)


def get_crop(session: Session, entity_id: Any) -> models.Crop | None:
    return get_entity(session, models.Crop, entity_id)


def get_device(session: Session, entity_id: Any) -> models.Device | None:
    return get_entity(session, models.Device, entity_id)


def get_sensor_reading(session: Session, entity_id: Any) -> models.SensorReading | None:
    return get_entity(session, models.SensorReading, entity_id)


def get_operation(session: Session, entity_id: Any) -> models.Operation | None:
    return get_entity(session, models.Operation, entity_id)


def update_field(session: Session, instance: models.Field, data: dict[str, Any]) -> models.Field:
    return update_entity(session, instance, data)


def update_crop(session: Session, instance: models.Crop, data: dict[str, Any]) -> models.Crop:
    return update_entity(session, instance, data)


def update_device(session: Session, instance: models.Device, data: dict[str, Any]) -> models.Device:
    return update_entity(session, instance, data)


def update_sensor_reading(
    session: Session, instance: models.SensorReading, data: dict[str, Any]
) -> models.SensorReading:
    return update_entity(session, instance, data)


def update_operation(session: Session, instance: models.Operation, data: dict[str, Any]) -> models.Operation:
    return update_entity(session, instance, data)


def delete_field(session: Session, instance: models.Field) -> None:
    delete_entity(session, instance)


def delete_crop(session: Session, instance: models.Crop) -> None:
    delete_entity(session, instance)


def delete_device(session: Session, instance: models.Device) -> None:
    delete_entity(session, instance)


def delete_sensor_reading(session: Session, instance: models.SensorReading) -> None:
    delete_entity(session, instance)


def delete_operation(session: Session, instance: models.Operation) -> None:
    delete_entity(session, instance)
