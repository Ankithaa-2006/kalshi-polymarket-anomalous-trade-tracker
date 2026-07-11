from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from ..database import get_db
from ..models.trader import Trader
from ..models.baseline import TraderBaseline

router = APIRouter()

@router.get("/leaderboard")
async def get_trader_leaderboard(
    platform: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Trader).join(TraderBaseline).options(
        joinedload(Trader.baseline)
    ).where(TraderBaseline.reputation_score.is_not(None))
    
    if platform and platform != 'all':
        stmt = stmt.where(Trader.platform == platform)
        
    stmt = stmt.order_by(TraderBaseline.reputation_score.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    traders = res.scalars().all()
    
    results = []
    for t in traders:
        baseline = t.baseline
        results.append({
            "id": t.id,
            "platform": t.platform,
            "external_trader_id": t.external_trader_id,
            "win_rate": float(baseline.win_rate) if baseline.win_rate else None,
            "large_bet_win_rate": float(baseline.large_bet_win_rate) if baseline.large_bet_win_rate else None,
            "reputation_score": float(baseline.reputation_score) if baseline.reputation_score else None,
            "total_resolved_bets": baseline.total_resolved_bets
        })
    return results
