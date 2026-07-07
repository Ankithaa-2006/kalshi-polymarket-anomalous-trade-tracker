from pydantic import BaseModel, ConfigDict
from typing import Optional

class AnomalyScoreResponse(BaseModel):
    bet_id: int
    self_score: Optional[float]
    market_score: Optional[float]
    lifecycle_weight: float
    composite_score: float
    flagged: bool
    scoring_mode: str
    model_config = ConfigDict(from_attributes=True)
