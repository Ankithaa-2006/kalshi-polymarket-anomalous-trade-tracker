from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .bet import FlaggedBetResponse

class TraderResponse(BaseModel):
    id: int
    platform: str
    external_trader_id: str
    model_config = ConfigDict(from_attributes=True)

class TraderHistoryResponse(BaseModel):
    trader: TraderResponse
    bets: List[FlaggedBetResponse]
    median_bet_size: Optional[float]
    mad_bet_size: Optional[float]
    win_rate: Optional[float]
    total_resolved_bets: int
