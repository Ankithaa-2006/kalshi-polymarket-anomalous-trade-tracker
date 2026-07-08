import logging
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timezone

from ..models.bet import Bet
from ..models.trader import Trader
from ..models.market import Market
from ..models.baseline import TraderBaseline, MarketBaseline
from ..models.calibration import CalibrationResult

logger = logging.getLogger(__name__)

async def compute_trader_baseline(session: AsyncSession, trader_id: int) -> None:
    """Computes median, MAD, and win-rate for a trader."""
    stmt = select(Bet.size).where(Bet.trader_id == trader_id)
    res = await session.execute(stmt)
    sizes = res.scalars().all()

    if not sizes:
        return

    sizes_arr = np.array(sizes, dtype=float)
    median_size = float(np.median(sizes_arr))
    mad_size = float(np.median(np.abs(sizes_arr - median_size)))
    # Prevent divide by zero issues later
    mad_size = max(mad_size, 1.0)

    # Compute win-rate (simplistic, based on calibration or resolved markets)
    # We can join Bet -> Market where resolved is true
    stmt_win = select(Bet.side, Market.resolved_outcome).join(Market).where(
        Bet.trader_id == trader_id,
        Market.resolved == True
    )
    res_win = await session.execute(stmt_win)
    resolved_bets = res_win.all()
    
    total_resolved = len(resolved_bets)
    wins = sum(1 for side, outcome in resolved_bets if side.lower() == (outcome or '').lower())
    win_rate = (wins / total_resolved) if total_resolved > 0 else None

    stmt_base = select(TraderBaseline).where(TraderBaseline.trader_id == trader_id)
    res_base = await session.execute(stmt_base)
    baseline = res_base.scalar_one_or_none()

    if baseline:
        baseline.median_bet_size = median_size
        baseline.mad_bet_size = mad_size
        baseline.win_rate = win_rate
        baseline.total_resolved_bets = total_resolved
        baseline.last_computed = datetime.now(timezone.utc)
    else:
        baseline = TraderBaseline(
            trader_id=trader_id,
            median_bet_size=median_size,
            mad_bet_size=mad_size,
            win_rate=win_rate,
            total_resolved_bets=total_resolved,
            last_computed=datetime.now(timezone.utc)
        )
        session.add(baseline)
    
    await session.commit()
    logger.debug(f"Computed baseline for trader {trader_id}: Median {median_size}, MAD {mad_size}")


async def compute_market_baseline(session: AsyncSession, market_id: int) -> None:
    """Computes median and MAD for a specific market across all traders."""
    stmt = select(Bet.size).where(Bet.market_id == market_id)
    res = await session.execute(stmt)
    sizes = res.scalars().all()

    if not sizes:
        return

    sizes_arr = np.array(sizes, dtype=float)
    median_size = float(np.median(sizes_arr))
    mad_size = float(np.median(np.abs(sizes_arr - median_size)))
    mad_size = max(mad_size, 1.0)

    stmt_base = select(MarketBaseline).where(MarketBaseline.market_id == market_id)
    res_base = await session.execute(stmt_base)
    baseline = res_base.scalar_one_or_none()

    if baseline:
        baseline.median_bet_size = median_size
        baseline.mad_bet_size = mad_size
        baseline.last_computed = datetime.now(timezone.utc)
    else:
        baseline = MarketBaseline(
            market_id=market_id,
            median_bet_size=median_size,
            mad_bet_size=mad_size,
            last_computed=datetime.now(timezone.utc)
        )
        session.add(baseline)

    await session.commit()
    logger.debug(f"Computed baseline for market {market_id}: Median {median_size}, MAD {mad_size}")
