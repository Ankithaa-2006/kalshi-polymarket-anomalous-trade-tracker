import numpy as np
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from ..database import async_session_maker
from ..models.trader import Trader
from ..models.baseline import TraderBaseline
from ..models.bet import Bet
from ..models.calibration import CalibrationResult

async def compute_reputations():
    """
    Computes `large_bet_win_rate` and `reputation_score` for all traders
    using empirical Bayesian shrinkage.
    """
    async with async_session_maker() as session:
        # First, compute global win rate to use as a prior
        stmt_global = select(CalibrationResult.correct).where(CalibrationResult.correct.is_not(None))
        res_global = await session.execute(stmt_global)
        all_results = res_global.scalars().all()
        
        if not all_results:
            return  # No resolved bets to base reputation on
            
        global_win_rate = sum(all_results) / len(all_results)
        
        # Bayesian shrinkage factor: higher C means we shrink more to the global average
        C = 10.0
        
        # Fetch all traders with baselines
        stmt_traders = select(TraderBaseline)
        res_traders = await session.execute(stmt_traders)
        baselines = res_traders.scalars().all()
        
        for baseline in baselines:
            # Recompute basic win_rate from resolved bets
            stmt_bets = select(Bet, CalibrationResult).join(
                CalibrationResult, Bet.id == CalibrationResult.bet_id
            ).where(Bet.trader_id == baseline.trader_id, CalibrationResult.correct.is_not(None))
            
            res_bets = await session.execute(stmt_bets)
            resolved_bets = res_bets.all()
            
            total_resolved = len(resolved_bets)
            if total_resolved == 0:
                continue
                
            wins = sum(1 for b, c in resolved_bets if c.correct)
            win_rate = wins / total_resolved
            
            # Compute large_bet_win_rate (bets > median_bet_size)
            median_size = baseline.median_bet_size
            if median_size is not None:
                large_bets = [c for b, c in resolved_bets if b.size > median_size]
                if large_bets:
                    large_wins = sum(1 for c in large_bets if c.correct)
                    large_bet_win_rate = large_wins / len(large_bets)
                else:
                    large_bet_win_rate = win_rate  # fallback
            else:
                large_bet_win_rate = win_rate
                
            # Bayesian reputation score: shrink toward global average
            reputation = ((win_rate * total_resolved) + (global_win_rate * C)) / (total_resolved + C)
            
            # Boost reputation slightly if their large bets perform significantly better
            if large_bet_win_rate > win_rate:
                reputation += 0.05 * (large_bet_win_rate - win_rate)
            
            # Update baseline
            baseline.win_rate = Decimal(str(win_rate))
            baseline.total_resolved_bets = total_resolved
            baseline.large_bet_win_rate = Decimal(str(large_bet_win_rate))
            baseline.reputation_score = Decimal(str(reputation))
            
        await session.commit()
