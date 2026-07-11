from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Watchlist(Base):
    __tablename__ = 'watchlists'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    watch_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'category' or 'trader'
    watch_value: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    user = relationship('User')

class AlertSent(Base):
    __tablename__ = 'alerts_sent'
    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey('watchlists.id'), nullable=False)
    bet_id: Mapped[int] = mapped_column(ForeignKey('bets.id'), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
