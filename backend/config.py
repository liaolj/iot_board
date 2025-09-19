"""Configuration helpers for database access."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class DatabaseSettings:
    """Database connection settings.

    Attributes
    ----------
    url:
        Full database URL. Defaults to a local PostgreSQL database. Any SQLAlchemy
        compatible URL is accepted.
    echo:
        Whether SQLAlchemy should log SQL statements.
    future:
        Whether to enable SQLAlchemy 2.0 style engine.
    """

    url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://iot:iot@localhost:5432/iot_board")
    echo: bool = bool(int(os.getenv("DATABASE_ECHO", "0")))
    future: bool = True


def get_database_settings() -> DatabaseSettings:
    """Return database settings loaded from environment variables."""

    return DatabaseSettings()
