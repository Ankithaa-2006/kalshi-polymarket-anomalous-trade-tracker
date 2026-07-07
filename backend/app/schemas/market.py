from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MarketBase(BaseModel):
    platform: str
    external_market_id: str
    title: Optional[str]
    category: Optional[str]
    open_date: Optional[datetime]
    resolution_date: Optional[datetime]
    resolved: bool
    resolved_outcome: Optional[str]

class MarketResponse(MarketBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MarketWithBaseline(MarketResponse):
    median_bet_size: Optional[float]
    mad_bet_size: Optional[float]
