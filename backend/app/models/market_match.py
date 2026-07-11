from sqlalchemy import Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from decimal import Decimal
from ..database import Base

class MarketMatch(Base):
    __tablename__ = 'market_matches'
    id: Mapped[int] = mapped_column(primary_key=True)
    market_id_a: Mapped[int] = mapped_column(ForeignKey('markets.id'), nullable=False)
    market_id_b: Mapped[int] = mapped_column(ForeignKey('markets.id'), nullable=False)
    similarity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships could be added if needed, but keeping it simple for now
