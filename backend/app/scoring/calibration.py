import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from decimal import Decimal

from ..models.bet import Bet
from ..models.market import Market
from ..models.anomaly import AnomalyScore
from ..models.calibration import CalibrationResult, CalibrationSummary
from ..database import async_session_maker

logger = logging.getLogger(__name__)

async def compute_calibration_for_market(session: AsyncSession, market_id: int) -> None:
    """Computes calibration for all flagged bets in a newly resolved market."""
    stmt_m = select(Market).where(Market.id == market_id)
    market = (await session.execute(stmt_m)).scalar_one_or_none()
    
    if not market or not market.resolved or not market.resolved_outcome:
        return
        
    actual_outcome = market.resolved_outcome.lower()
    
    stmt_b = select(Bet).join(AnomalyScore).where(
        Bet.market_id == market_id,
        AnomalyScore.flagged == True
    )
    bets = (await session.execute(stmt_b)).scalars().all()
    
    for bet in bets:
        predicted_side = bet.side.lower()
        correct = (predicted_side == actual_outcome)
        
        stmt_c = select(CalibrationResult).where(CalibrationResult.bet_id == bet.id)
        cal = (await session.execute(stmt_c)).scalar_one_or_none()
        
        if cal:
            cal.predicted_side = predicted_side
            cal.actual_outcome = actual_outcome
            cal.correct = correct
            cal.computed_at = datetime.now(timezone.utc)
        else:
            cal = CalibrationResult(
                bet_id=bet.id,
                predicted_side=predicted_side,
                actual_outcome=actual_outcome,
                correct=correct,
                computed_at=datetime.now(timezone.utc)
            )
            session.add(cal)
            
    await session.commit()
    logger.info(f"Computed calibration for {len(bets)} flagged bets in market {market_id}.")

async def update_calibration_summary() -> None:
    """Rebuilds the CalibrationSummary table grouping by category and confidence_tier."""
    async with async_session_maker() as session:
        # Clear existing summary
        await session.execute("DELETE FROM calibration_summary")
        
        stmt = select(CalibrationResult, AnomalyScore, Market).join(
            Bet, CalibrationResult.bet_id == Bet.id
        ).join(
            AnomalyScore, Bet.id == AnomalyScore.bet_id
        ).join(
            Market, Bet.market_id == Market.id
        ).where(CalibrationResult.correct.is_not(None))
        
        res = await session.execute(stmt)
        records = res.all()
        
        if not records:
            return
            
        from collections import defaultdict
        # Group by (scope, confidence_tier)
        # scope is either 'global' or the market.category
        groups = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for cal, anomaly, market in records:
            correct = cal.correct
            tier = anomaly.confidence_tier
            cat = market.category or 'uncategorized'
            
            # Global group
            groups[('global', tier)]['total'] += 1
            if correct:
                groups[('global', tier)]['wins'] += 1
                
            groups[('global', 'all')]['total'] += 1
            if correct:
                groups[('global', 'all')]['wins'] += 1
                
            # Category group
            groups[(cat, tier)]['total'] += 1
            if correct:
                groups[(cat, tier)]['wins'] += 1
                
            groups[(cat, 'all')]['total'] += 1
            if correct:
                groups[(cat, 'all')]['wins'] += 1
                
        for (scope, tier), stats in groups.items():
            hit_rate = stats['wins'] / stats['total'] if stats['total'] > 0 else 0
            summary = CalibrationSummary(
                scope=scope,
                confidence_tier=tier if tier != 'all' else None,
                hit_rate=Decimal(str(hit_rate)),
                sample_size=stats['total']
            )
            session.add(summary)
            
        await session.commit()
        logger.info(f"Updated calibration_summary with {len(groups)} aggregated rows.")
