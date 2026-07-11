from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from ..database import get_db
from ..models.calibration import CalibrationSummary
from ..schemas.calibration import CalibrationSummaryResponse

router = APIRouter()

@router.get("/summary", response_model=List[CalibrationSummaryResponse])
async def get_calibration_summary(
    scope: Optional[str] = None,
    confidence_tier: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    stmt = select(CalibrationSummary)
    
    if scope:
        stmt = stmt.where(CalibrationSummary.scope == scope)
    if confidence_tier:
        stmt = stmt.where(CalibrationSummary.confidence_tier == confidence_tier)
        
    res = await session.execute(stmt)
    summaries = res.scalars().all()
    
    results = []
    for s in summaries:
        results.append({
            "total_flagged": s.sample_size,
            "correct": int(float(s.hit_rate) * s.sample_size) if s.hit_rate else 0,
            "hit_rate": float(s.hit_rate) if s.hit_rate else 0.0,
            "score_range": "All",
            "scope": s.scope,
            "confidence_tier": s.confidence_tier,
            "sample_size": s.sample_size
        })
    return results
