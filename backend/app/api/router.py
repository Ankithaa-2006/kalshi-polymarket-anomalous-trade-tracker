from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from ..database import get_db
from ..models.bet import Bet
from ..models.market import Market
from ..models.trader import Trader
from ..models.anomaly import AnomalyScore
from ..models.calibration import CalibrationResult
from ..models.baseline import TraderBaseline, MarketBaseline
from ..schemas.bet import FlaggedBetResponse, BetDetailResponse
from ..schemas.market import MarketWithBaseline
from ..schemas.calibration import CalibrationSummaryResponse

api_router = APIRouter()

@api_router.get("/bets/flagged", response_model=List[FlaggedBetResponse])
async def get_flagged_bets(
    platform: Optional[str] = None,
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
        
    stmt = stmt.order_by(AnomalyScore.composite_score.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    bets = res.scalars().all()
    
    results = []
    for bet in bets:
        # manual mapping to Flattened schema
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
            "composite_score": float(anomaly.composite_score),
            "scoring_mode": anomaly.scoring_mode,
            "market_title": bet.market.title,
            "platform": bet.market.platform,
            "category": bet.market.category,
            "trader_win_rate": float(trader_win_rate) if trader_win_rate is not None else None,
            "calibration_hit_rate": None, # Should be calculated at runtime or fetched from aggregations
            "calibration_sample_size": None
        })
    
    return results

@api_router.get("/calibration/summary", response_model=CalibrationSummaryResponse)
async def get_calibration_summary(
    platform: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    stmt = select(CalibrationResult).join(Bet).join(Market)
    if platform and platform != 'all':
        stmt = stmt.where(Market.platform == platform)
        
    res = await session.execute(stmt)
    results = res.scalars().all()
    
    total = len(results)
    correct = sum(1 for r in results if r.correct)
    hit_rate = (correct / total) if total > 0 else 0.0
    
    return {
        "total_flagged": total,
        "correct": correct,
        "hit_rate": hit_rate,
        "score_range": "All",
        "platform": platform,
        "caveat": "Low sample size" if total < 100 else None
    }
