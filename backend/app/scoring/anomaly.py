import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from decimal import Decimal

from ..models.bet import Bet
from ..models.baseline import TraderBaseline, MarketBaseline
from ..models.anomaly import AnomalyScore
from ..models.market_match import MarketMatch
from ..alerting.dispatcher import dispatch_alerts
from ..config import settings

logger = logging.getLogger(__name__)

async def compute_anomaly_score(session: AsyncSession, bet_id: int) -> None:
    """Computes the anomaly score for a single bet based on baselines and cross-platform matches."""
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
        deviation = float(bet.size) - float(trader_base.median_bet_size)
        self_score = deviation / float(trader_base.mad_bet_size)
        self_score = max(0, self_score)

    # Calculate market score
    market_score = None
    if market_base and market_base.mad_bet_size > 0:
        deviation = float(bet.size) - float(market_base.median_bet_size)
        market_score = deviation / float(market_base.mad_bet_size)
        market_score = max(0, market_score)

    # Lifecycle weight
    lifecycle_weight = 1.0
    if bet.time_to_resolution_hours is not None:
        t_hrs = float(bet.time_to_resolution_hours)
        if t_hrs < 24:
            lifecycle_weight = 2.0
        elif t_hrs < 72:
            lifecycle_weight = 1.5

    # Cross-Platform Corroboration
    cross_platform_corroboration = 0.0
    stmt_match = select(MarketMatch).where(
        ((MarketMatch.market_id_a == bet.market_id) | (MarketMatch.market_id_b == bet.market_id))
    ).order_by(MarketMatch.similarity_score.desc()).limit(1)
    match_res = await session.execute(stmt_match)
    match = match_res.scalar_one_or_none()
    
    if match:
        other_market_id = match.market_id_b if match.market_id_a == bet.market_id else match.market_id_a
        # Check for recently flagged bets on the other market
        stmt_other_flags = select(Bet.id).join(AnomalyScore).where(
            Bet.market_id == other_market_id,
            AnomalyScore.flagged == True
        ).limit(1)
        other_res = await session.execute(stmt_other_flags)
        if other_res.scalar_one_or_none():
            cross_platform_corroboration = 1.0 # arbitrary boost

    # Composite Score
    scoring_mode = 'market_only'
    composite_score = 0.0
    
    if self_score is not None and market_score is not None:
        scoring_mode = 'full'
        composite_score = ((self_score * 0.6) + (market_score * 0.4)) * lifecycle_weight
    elif market_score is not None:
        composite_score = market_score * lifecycle_weight
    elif self_score is not None:
        composite_score = self_score * lifecycle_weight
        
    composite_score += cross_platform_corroboration

    flagged = composite_score >= settings.ANOMALY_THRESHOLD
    
    # Confidence Tier
    confidence_tier = 'low'
    if flagged:
        if composite_score >= settings.ANOMALY_THRESHOLD + 2.0:
            confidence_tier = 'high'
        else:
            confidence_tier = 'medium'

    # Update or insert AnomalyScore
    stmt_as = select(AnomalyScore).where(AnomalyScore.bet_id == bet_id)
    anomaly = (await session.execute(stmt_as)).scalar_one_or_none()

    if anomaly:
        anomaly.self_score = Decimal(str(self_score)) if self_score is not None else None
        anomaly.market_score = Decimal(str(market_score)) if market_score is not None else None
        anomaly.lifecycle_weight = Decimal(str(lifecycle_weight))
        anomaly.cross_platform_corroboration = Decimal(str(cross_platform_corroboration))
        anomaly.composite_score = Decimal(str(composite_score))
        anomaly.confidence_tier = confidence_tier
        anomaly.flagged = flagged
        anomaly.scoring_mode = scoring_mode
    else:
        anomaly = AnomalyScore(
            bet_id=bet_id,
            self_score=Decimal(str(self_score)) if self_score is not None else None,
            market_score=Decimal(str(market_score)) if market_score is not None else None,
            lifecycle_weight=Decimal(str(lifecycle_weight)),
            cross_platform_corroboration=Decimal(str(cross_platform_corroboration)),
            composite_score=Decimal(str(composite_score)),
            confidence_tier=confidence_tier,
            flagged=flagged,
            scoring_mode=scoring_mode
        )
        session.add(anomaly)
    
    await session.commit()
    logger.info(f"Computed anomaly score for bet {bet_id}: {composite_score} (Tier: {confidence_tier})")
    
    if flagged:
        # Trigger alerting dispatcher in the background
        loop = asyncio.get_running_loop()
        loop.create_task(dispatch_alerts(bet_id))
