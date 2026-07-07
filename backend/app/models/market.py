from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from ..database import Base

class Market(Base):
    __tablename__ = 'markets'
    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)  # 'kalshi' or 'polymarket'
    external_market_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    open_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolution_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_outcome: Mapped[Optional[str]] = mapped_column(String(20))  # 'yes'/'no'/null
    
    __table_args__ = (UniqueConstraint('platform', 'external_market_id', name='uq_market_platform_id'),)
    
    # Relationships
    bets = relationship('Bet', back_populates='market')
    baseline = relationship('MarketBaseline', back_populates='market', uselist=False)
