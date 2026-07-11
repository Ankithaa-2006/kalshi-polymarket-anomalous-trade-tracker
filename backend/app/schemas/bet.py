from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BetBase(BaseModel):
    market_id: int
    trader_id: Optional[int]
    side: str
    size: float
    price: float
    bet_timestamp: datetime
    time_to_resolution_hours: Optional[float]

class BetResponse(BetBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FlaggedBetResponse(BetResponse):
    self_score: Optional[float]
    market_score: Optional[float]
    lifecycle_weight: float
    composite_score: float
    cross_platform_corroboration: Optional[float] = None
    confidence_tier: Optional[str] = None
    scoring_mode: str
    market_title: Optional[str]
    platform: str
    category: Optional[str]
    trader_win_rate: Optional[float]
    calibration_hit_rate: Optional[float]
    calibration_sample_size: Optional[int]

class BetDetailResponse(FlaggedBetResponse):
    # We can add relationships here later, like news_events
    pass
