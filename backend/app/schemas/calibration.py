from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CalibrationResultResponse(BaseModel):
    id: int
    bet_id: int
    predicted_side: str
    actual_outcome: Optional[str]
    correct: Optional[bool]
    computed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CalibrationSummaryResponse(BaseModel):
    total_flagged: int
    correct: int
    hit_rate: float
    score_range: str
    platform: Optional[str] = None
    category: Optional[str] = None
    caveat: Optional[str] = None
    
    # NEW fields from materialized table
    scope: Optional[str] = None
    confidence_tier: Optional[str] = None
    sample_size: Optional[int] = None
