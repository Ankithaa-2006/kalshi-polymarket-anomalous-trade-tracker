from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

from ..database import get_db
from ..models.market import Market
from ..models.market_match import MarketMatch
from ..schemas.market_match import MarketMatchResponse

router = APIRouter()

@router.get("/{market_id}/matches", response_model=List[MarketMatchResponse])
async def get_market_matches(market_id: int, session: AsyncSession = Depends(get_db)):
    stmt = select(MarketMatch).where(
        (MarketMatch.market_id_a == market_id) | (MarketMatch.market_id_b == market_id)
    ).order_by(MarketMatch.similarity_score.desc())
    
    res = await session.execute(stmt)
    return res.scalars().all()
