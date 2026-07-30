from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.odor_prediction import OdorPrediction


class OdorEnvData(Base):
    """Environmental sensor readings used as input for odor analysis and prediction."""

    __tablename__ = "odor_env_data"
    __table_args__ = (
        Index("ix_odor_env_data_measured_at", "measured_at"),
        Index("ix_odor_env_data_site_id", "site_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="Primary key")

    site_id: Mapped[str] = mapped_column(
        String(64),
        comment="Monitoring site or facility identifier",
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="Timestamp when the environmental data was measured",
    )

    temperature: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Ambient temperature in degrees Celsius",
    )
    humidity: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Relative humidity as a percentage",
    )
    wind_speed: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Wind speed in meters per second",
    )
    wind_direction: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Wind direction in degrees from north",
    )
    pressure: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Atmospheric pressure in hectopascals",
    )

    h2s: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Hydrogen sulfide concentration in ppm",
    )
    nh3: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Ammonia concentration in ppm",
    )
    voc: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Volatile organic compound concentration in ppm",
    )
    odor_intensity: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Observed odor intensity or odor unit value",
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(32),
        comment="Data source identifier, such as sensor or simulator",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Record creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Record last update timestamp",
    )

    predictions: Mapped[list[OdorPrediction]] = relationship(
        back_populates="env_data",
    )
