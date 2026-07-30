from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.odor_prediction import OdorPrediction


class ModelHistory(Base):
    """Metadata for trained ML models and their lifecycle."""

    __tablename__ = "model_history"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Primary key")

    model_name: Mapped[str] = mapped_column(
        String(128),
        comment="Human-readable model name",
    )
    version: Mapped[str] = mapped_column(
        String(64),
        comment="Model version identifier",
    )
    file_path: Mapped[str] = mapped_column(
        String(512),
        comment="Filesystem path to the saved model artifact",
    )

    status: Mapped[str] = mapped_column(
        String(32),
        server_default="trained",
        comment="Model lifecycle status, such as training, active, or archived",
    )

    training_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Training start timestamp",
    )
    training_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Training completion timestamp",
    )

    train_loss: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Final training loss value",
    )
    validation_loss: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Final validation loss value",
    )
    metrics: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Serialized evaluation metrics, such as JSON",
    )
    hyperparameters: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Serialized training hyperparameters, such as JSON",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Optional free-text notes about the training run",
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
        back_populates="model_history",
    )
