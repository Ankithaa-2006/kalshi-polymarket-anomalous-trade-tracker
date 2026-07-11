from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WatchlistBase(BaseModel):
    watch_type: str
    watch_value: str

class WatchlistCreate(WatchlistBase):
    user_id: int

class WatchlistResponse(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
