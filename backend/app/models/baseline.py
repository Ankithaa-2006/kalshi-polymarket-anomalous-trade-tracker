from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ..database import Base

class TraderBaseline(Base):
    __tablename__ = 'trader_baselines'
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id'), primary_key=True)
    median_bet_size: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    mad_bet_size: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    win_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    total_resolved_bets: Mapped[int] = mapped_column(Integer, default=0)
    large_bet_win_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    reputation_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    last_computed: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    trader = relationship('Trader', back_populates='baseline')

class MarketBaseline(Base):
    __tablename__ = 'market_baselines'
    market_id: Mapped[int] = mapped_column(ForeignKey('markets.id'), primary_key=True)
    median_bet_size: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    mad_bet_size: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    last_computed: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    market = relationship('Market', back_populates='baseline')
