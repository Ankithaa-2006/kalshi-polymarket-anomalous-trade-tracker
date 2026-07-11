from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MarketMatchResponse(BaseModel):
    id: int
    market_id_a: int
    market_id_b: int
    similarity_score: Optional[float]
    confirmed: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
