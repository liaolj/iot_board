"""SQLAlchemy models describing the IoT agriculture domain."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for all ORM models."""


class Field(Base):
    """Represents a specific field/plot under management."""

    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    crops: Mapped[list["Crop"]] = relationship("Crop", back_populates="field", cascade="all, delete-orphan")
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="field", cascade="all, delete-orphan"
    )
    operations: Mapped[list["Operation"]] = relationship(
        "Operation", back_populates="field", cascade="all, delete-orphan"
    )


class Crop(Base):
    """Represents a crop planted in a field."""

    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(255), nullable=True)
    planting_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    growth_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expected_harvest_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    field: Mapped[Field] = relationship("Field", back_populates="crops")
    operations: Mapped[list["Operation"]] = relationship("Operation", back_populates="crop")


class Device(Base):
    """Represents an IoT device installed in a field."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    field: Mapped[Field | None] = relationship("Field", back_populates="devices")
    sensor_readings: Mapped[list["SensorReading"]] = relationship(
        "SensorReading", back_populates="device", cascade="all, delete-orphan"
    )


class SensorReading(Base):
    """Represents a sensor reading from a device."""

    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    device: Mapped[Device] = relationship("Device", back_populates="sensor_readings")


class Operation(Base):
    """Represents an operation performed on a field/crop."""

    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="SET NULL"), nullable=True)
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("crops.id", ondelete="SET NULL"), nullable=True)
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    operator: Mapped[str | None] = mapped_column(String(100), nullable=True)

    field: Mapped[Field | None] = relationship("Field", back_populates="operations")
    crop: Mapped[Crop | None] = relationship("Crop", back_populates="operations")
