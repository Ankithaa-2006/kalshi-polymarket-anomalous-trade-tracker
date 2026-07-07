from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ..database import Base

class Bet(Base):
    __tablename__ = 'bets'
    id: Mapped[int] = mapped_column(primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey('markets.id'), nullable=False)
    trader_id: Mapped[Optional[int]] = mapped_column(ForeignKey('traders.id'), nullable=True)  # null for Kalshi public trades
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # 'yes' / 'no'
    size: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # implied probability
    bet_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    time_to_resolution_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    market = relationship('Market', back_populates='bets')
    trader = relationship('Trader', back_populates='bets')
    anomaly_score = relationship('AnomalyScore', back_populates='bet', uselist=False)
    news_events = relationship('NewsEvent', back_populates='bet')
    calibration_result = relationship('CalibrationResult', back_populates='bet', uselist=False)
