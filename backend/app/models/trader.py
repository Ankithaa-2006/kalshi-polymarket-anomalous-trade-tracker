from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class Trader(Base):
    __tablename__ = 'traders'
    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    external_trader_id: Mapped[str] = mapped_column(String(255), nullable=False)  # wallet addr or account id
    
    __table_args__ = (UniqueConstraint('platform', 'external_trader_id', name='uq_trader_platform_id'),)
    
    bets = relationship('Bet', back_populates='trader')
    baseline = relationship('TraderBaseline', back_populates='trader', uselist=False)
