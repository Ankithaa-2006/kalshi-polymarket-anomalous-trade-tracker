from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ..database import Base

class NewsEvent(Base):
    __tablename__ = 'news_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    bet_id: Mapped[int] = mapped_column(ForeignKey('bets.id'), nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    url: Mapped[Optional[str]] = mapped_column(Text)
    relevance_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20))  # positive/negative/neutral
    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))  # -1.0 to 1.0
    event_category: Mapped[Optional[str]] = mapped_column(String(50))  # policy, election, etc.
    
    bet = relationship('Bet', back_populates='news_events')
