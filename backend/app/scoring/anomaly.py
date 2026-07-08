import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from decimal import Decimal

from ..models.bet import Bet
from ..models.baseline import TraderBaseline, MarketBaseline
from ..models.anomaly import AnomalyScore
from ..config import settings

logger = logging.getLogger(__name__)

async def compute_anomaly_score(session: AsyncSession, bet_id: int) -> None:
    """Computes the anomaly score for a single bet based on baselines."""
    stmt = select(Bet).where(Bet.id == bet_id).options(
        joinedload(Bet.market),
        joinedload(Bet.trader)
    )
    res = await session.execute(stmt)
    bet = res.scalar_one_or_none()
    
    if not bet:
        return

    # Get trader baseline
    trader_base = None
    if bet.trader_id:
        stmt_tb = select(TraderBaseline).where(TraderBaseline.trader_id == bet.trader_id)
        trader_base = (await session.execute(stmt_tb)).scalar_one_or_none()

    # Get market baseline
    stmt_mb = select(MarketBaseline).where(MarketBaseline.market_id == bet.market_id)
    market_base = (await session.execute(stmt_mb)).scalar_one_or_none()

    # Calculate self score
    self_score = None
    if trader_base and trader_base.mad_bet_size > 0:
        # Z-score-like calculation based on MAD
        deviation = float(bet.size) - float(trader_base.median_bet_size)
        self_score = deviation / float(trader_base.mad_bet_size)
        self_score = max(0, self_score) # only care about unusually large

    # Calculate market score
    market_score = None
    if market_base and market_base.mad_bet_size > 0:
        deviation = float(bet.size) - float(market_base.median_bet_size)
        market_score = deviation / float(market_base.mad_bet_size)
        market_score = max(0, market_score)

    # Lifecycle weight (close to resolution = higher weight)
    lifecycle_weight = 1.0
    if bet.time_to_resolution_hours is not None:
        t_hrs = float(bet.time_to_resolution_hours)
        if t_hrs < 24:
            lifecycle_weight = 2.0
        elif t_hrs < 72:
            lifecycle_weight = 1.5

    # Composite Score
    scoring_mode = 'market_only'
    composite_score = 0.0
    
    if self_score is not None and market_score is not None:
        scoring_mode = 'full'
        # Weighted combination
        composite_score = ((self_score * 0.6) + (market_score * 0.4)) * lifecycle_weight
    elif market_score is not None:
        composite_score = market_score * lifecycle_weight
    elif self_score is not None:
        composite_score = self_score * lifecycle_weight
        
    flagged = composite_score >= settings.ANOMALY_THRESHOLD

    # Update or insert AnomalyScore
    stmt_as = select(AnomalyScore).where(AnomalyScore.bet_id == bet_id)
    anomaly = (await session.execute(stmt_as)).scalar_one_or_none()

    if anomaly:
        anomaly.self_score = self_score
        anomaly.market_score = market_score
        anomaly.lifecycle_weight = lifecycle_weight
        anomaly.composite_score = composite_score
        anomaly.flagged = flagged
        anomaly.scoring_mode = scoring_mode
    else:
        anomaly = AnomalyScore(
            bet_id=bet_id,
            self_score=self_score,
            market_score=market_score,
            lifecycle_weight=lifecycle_weight,
            composite_score=composite_score,
            flagged=flagged,
            scoring_mode=scoring_mode
        )
        session.add(anomaly)
    
    await session.commit()
    logger.info(f"Computed anomaly score for bet {bet_id}: {composite_score} (Flagged: {flagged})")
