import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

from ..models.bet import Bet
from ..models.market import Market
from ..models.anomaly import AnomalyScore
from ..models.calibration import CalibrationResult

logger = logging.getLogger(__name__)

async def compute_calibration_for_market(session: AsyncSession, market_id: int) -> None:
    """Computes calibration for all flagged bets in a newly resolved market."""
    # Find the market
    stmt_m = select(Market).where(Market.id == market_id)
    market = (await session.execute(stmt_m)).scalar_one_or_none()
    
    if not market or not market.resolved or not market.resolved_outcome:
        return
        
    actual_outcome = market.resolved_outcome.lower()
    
    # Find all flagged bets for this market
    stmt_b = select(Bet).join(AnomalyScore).where(
        Bet.market_id == market_id,
        AnomalyScore.flagged == True
    )
    bets = (await session.execute(stmt_b)).scalars().all()
    
    for bet in bets:
        predicted_side = bet.side.lower()
        correct = (predicted_side == actual_outcome)
        
        # Upsert calibration result
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
