from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NewsEventResponse(BaseModel):
    id: int
    bet_id: int
    headline: str
    source: Optional[str]
    published_at: Optional[datetime]
    url: Optional[str]
    relevance_score: Optional[float]
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    event_category: Optional[str]
    model_config = ConfigDict(from_attributes=True)
