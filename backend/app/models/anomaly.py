from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from typing import Optional
from ..database import Base

class AnomalyScore(Base):
    __tablename__ = 'anomaly_scores'
    bet_id: Mapped[int] = mapped_column(ForeignKey('bets.id'), primary_key=True)
    self_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))  # null if insufficient history
    market_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    lifecycle_weight: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=1.0)
    composite_score: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    scoring_mode: Mapped[str] = mapped_column(String(20), default='market_only')  # 'full' or 'market_only'
    
    bet = relationship('Bet', back_populates='anomaly_score')
