from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from ..database import get_db
from ..models.bet import Bet
from ..models.market import Market
from ..models.trader import Trader
from ..models.anomaly import AnomalyScore
from ..schemas.bet import FlaggedBetResponse

router = APIRouter()

@router.get("/flagged", response_model=List[FlaggedBetResponse])
async def get_flagged_bets(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    confidence_tier: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Bet).join(AnomalyScore).join(Market).options(
        joinedload(Bet.anomaly_score),
        joinedload(Bet.market),
        joinedload(Bet.trader).joinedload(Trader.baseline)
    ).where(AnomalyScore.flagged == True)
    
    if platform and platform != 'all':
        stmt = stmt.where(Market.platform == platform)
    if category:
        stmt = stmt.where(Market.category == category)
    if confidence_tier:
        stmt = stmt.where(AnomalyScore.confidence_tier == confidence_tier)
        
    stmt = stmt.order_by(AnomalyScore.composite_score.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    bets = res.scalars().all()
    
    results = []
    for bet in bets:
        anomaly = bet.anomaly_score
        trader_win_rate = bet.trader.baseline.win_rate if (bet.trader and bet.trader.baseline) else None
        
        results.append({
            "id": bet.id,
            "market_id": bet.market_id,
            "trader_id": bet.trader_id,
            "side": bet.side,
            "size": float(bet.size),
            "price": float(bet.price),
            "bet_timestamp": bet.bet_timestamp,
            "time_to_resolution_hours": float(bet.time_to_resolution_hours) if bet.time_to_resolution_hours else None,
            "created_at": bet.created_at,
            "self_score": float(anomaly.self_score) if anomaly.self_score else None,
            "market_score": float(anomaly.market_score) if anomaly.market_score else None,
            "lifecycle_weight": float(anomaly.lifecycle_weight),
            "cross_platform_corroboration": float(anomaly.cross_platform_corroboration) if anomaly.cross_platform_corroboration else None,
            "composite_score": float(anomaly.composite_score),
            "confidence_tier": anomaly.confidence_tier,
            "scoring_mode": anomaly.scoring_mode,
            "market_title": bet.market.title,
            "platform": bet.market.platform,
            "category": bet.market.category,
            "trader_win_rate": float(trader_win_rate) if trader_win_rate is not None else None,
            "calibration_hit_rate": None,
            "calibration_sample_size": None
        })
    
    return results

@router.get("/{bet_id}/explain")
async def get_bet_explain(bet_id: int, session: AsyncSession = Depends(get_db)):
    stmt = select(AnomalyScore).where(AnomalyScore.bet_id == bet_id)
    res = await session.execute(stmt)
    score = res.scalar_one_or_none()
    
    if not score:
        raise HTTPException(status_code=404, detail="Anomaly score not found")
        
    return {
        "self_score": float(score.self_score) if score.self_score else 0,
        "market_score": float(score.market_score) if score.market_score else 0,
        "lifecycle_weight": float(score.lifecycle_weight) if score.lifecycle_weight else 1,
        "cross_platform_corroboration": float(score.cross_platform_corroboration) if score.cross_platform_corroboration else 0,
        "composite_score": float(score.composite_score) if score.composite_score else 0,
    }
