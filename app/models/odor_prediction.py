from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.model_history import ModelHistory
    from app.models.odor_env_data import OdorEnvData


class OdorPrediction(Base):
    """Odor prediction results produced by an ML model from environmental data."""

    __tablename__ = "odor_prediction"
    __table_args__ = (
        Index("ix_odor_prediction_predicted_at", "predicted_at"),
        Index("ix_odor_prediction_env_data_id", "env_data_id"),
        Index("ix_odor_prediction_model_history_id", "model_history_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="Primary key")

    env_data_id: Mapped[int] = mapped_column(
        ForeignKey("odor_env_data.id", ondelete="CASCADE"),
        comment="Reference to the source environmental data record",
    )
    model_history_id: Mapped[int] = mapped_column(
        ForeignKey("model_history.id", ondelete="RESTRICT"),
        comment="Reference to the model version used for inference",
    )

    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="Timestamp when the prediction was generated",
    )

    predicted_odor_intensity: Mapped[float] = mapped_column(
        Float,
        comment="Predicted odor intensity or odor unit value",
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Model confidence score between 0 and 1",
    )
    prediction_label: Mapped[Optional[str]] = mapped_column(
        String(64),
        comment="Optional categorical prediction label",
    )
    details: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Optional serialized prediction details, such as JSON",
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

    env_data: Mapped[OdorEnvData] = relationship(
        back_populates="predictions",
    )
    model_history: Mapped[ModelHistory] = relationship(
        back_populates="predictions",
    )
