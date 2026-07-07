import httpx
from datetime import datetime, timezone
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from ..models.market import Market
from ..models.trader import Trader
from ..models.bet import Bet

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"
DATA_API_URL = "https://data-api.polymarket.com"

async def fetch_active_markets(session: AsyncSession) -> None:
    """Fetch active markets from Gamma API and upsert into DB."""
    async with httpx.AsyncClient() as client:
        url = f"{GAMMA_API_URL}/markets?active=true&closed=false"
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                external_id = item.get("conditionId")
                if not external_id:
                    continue
                
                # Check if market exists
                stmt = select(Market).where(
                    Market.platform == 'polymarket',
                    Market.external_market_id == external_id
                )
                result = await session.execute(stmt)
                market = result.scalar_one_or_none()
                
                open_date = item.get("startDate")
                res_date = item.get("endDate")
                
                if market is None:
                    market = Market(
                        platform='polymarket',
                        external_market_id=external_id,
                        title=item.get("question"),
                        category=None, # Tags could be mapped here if needed
                        open_date=datetime.fromisoformat(open_date.replace("Z", "+00:00")) if open_date else None,
                        resolution_date=datetime.fromisoformat(res_date.replace("Z", "+00:00")) if res_date else None,
                        resolved=False,
                        resolved_outcome=None
                    )
                    session.add(market)
                else:
                    market.title = item.get("question")
                    if res_date:
                        market.resolution_date = datetime.fromisoformat(res_date.replace("Z", "+00:00"))
            
            await session.commit()
            logger.info("Successfully fetched and updated active Polymarket markets.")
        except Exception as e:
            logger.error(f"Error fetching Polymarket markets: {e}")
            await session.rollback()

async def fetch_resolved_markets(session: AsyncSession) -> None:
    """Fetch recently closed markets to update resolution status."""
    # Similar logic fetching closed=true and updating the DB
    pass

async def fetch_wallet_trades(session: AsyncSession, wallet_address: str) -> None:
    """Fetch trades for a specific wallet from Data API."""
    async with httpx.AsyncClient() as client:
        url = f"{DATA_API_URL}/trades?user={wallet_address}"
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            # Process trades, map to markets, and create Bet entries
            # Compute time_to_resolution_hours
            
            # This is a stub for now. We need the exact trade schema.
            pass
        except Exception as e:
            logger.error(f"Error fetching trades for {wallet_address}: {e}")
