from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from ..database import Base

class CalibrationResult(Base):
    __tablename__ = 'calibration_results'
    id: Mapped[int] = mapped_column(primary_key=True)
    bet_id: Mapped[int] = mapped_column(ForeignKey('bets.id'), nullable=False)
    predicted_side: Mapped[str] = mapped_column(String(10), nullable=False)
    actual_outcome: Mapped[Optional[str]] = mapped_column(String(10))
    correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    bet = relationship('Bet', back_populates='calibration_result')
