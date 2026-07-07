import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from app.database import Base
from app.models import (
    Market, Trader, Bet, TraderBaseline, MarketBaseline,
    AnomalyScore, NewsEvent, CalibrationResult
)

logger = logging.getLogger(__name__)

async def seed_db(session: AsyncSession):
    # Markets
    m1 = Market(
        platform='polymarket',
        external_market_id='0x123456789',
        title='Will the Fed cut rates in September 2026?',
        category='economics',
        open_date=datetime.now(timezone.utc) - timedelta(days=30),
        resolution_date=datetime.now(timezone.utc) + timedelta(days=5),
        resolved=False,
    )
    m2 = Market(
        platform='kalshi',
        external_market_id='MIDTERMS-26',
        title='Who will win the 2026 Midterms?',
        category='politics',
        open_date=datetime.now(timezone.utc) - timedelta(days=60),
        resolution_date=datetime.now(timezone.utc) + timedelta(days=90),
        resolved=False,
    )
    session.add_all([m1, m2])
    await session.commit()

    # Traders
    t1 = Trader(platform='polymarket', external_trader_id='0xABCDEF123456')
    session.add(t1)
    await session.commit()

    # Baselines
    tb1 = TraderBaseline(
        trader_id=t1.id,
        median_bet_size=Decimal('1000.00'),
        mad_bet_size=Decimal('250.00'),
        win_rate=Decimal('0.6500'),
        total_resolved_bets=142
    )
    mb1 = MarketBaseline(
        market_id=m1.id,
        median_bet_size=Decimal('500.00'),
        mad_bet_size=Decimal('150.00')
    )
    mb2 = MarketBaseline(
        market_id=m2.id,
        median_bet_size=Decimal('100.00'),
        mad_bet_size=Decimal('30.00')
    )
    session.add_all([tb1, mb1, mb2])
    await session.commit()

    # Bets
    b1 = Bet(
        market_id=m1.id,
        trader_id=t1.id,
        side='yes',
        size=Decimal('250000.00'),
        price=Decimal('0.7500'),
        bet_timestamp=datetime.now(timezone.utc) - timedelta(hours=4, minutes=30),
        time_to_resolution_hours=Decimal('4.5')
    )
    session.add(b1)
    await session.commit()

    # Anomaly
    a1 = AnomalyScore(
        bet_id=b1.id,
        self_score=Decimal('4.1'),
        market_score=Decimal('3.8'),
        lifecycle_weight=Decimal('1.5'),
        composite_score=Decimal('5.2'),
        flagged=True,
        scoring_mode='full'
    )
    session.add(a1)
    await session.commit()

async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        await seed_db(session)
    print("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(main())
