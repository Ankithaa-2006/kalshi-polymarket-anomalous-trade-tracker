from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..database import get_db
from ..models.user import User, Watchlist
from ..schemas.user import WatchlistCreate, WatchlistResponse

router = APIRouter()

@router.post("/", response_model=WatchlistResponse)
async def create_watchlist(watchlist: WatchlistCreate, session: AsyncSession = Depends(get_db)):
    # Simple creation, assumes user_id exists
    new_watch = Watchlist(
        user_id=watchlist.user_id,
        watch_type=watchlist.watch_type,
        watch_value=watchlist.watch_value
    )
    session.add(new_watch)
    await session.commit()
    await session.refresh(new_watch)
    return new_watch

@router.get("/{user_id}", response_model=List[WatchlistResponse])
async def get_watchlists(user_id: int, session: AsyncSession = Depends(get_db)):
    stmt = select(Watchlist).where(Watchlist.user_id == user_id)
    res = await session.execute(stmt)
    return res.scalars().all()
