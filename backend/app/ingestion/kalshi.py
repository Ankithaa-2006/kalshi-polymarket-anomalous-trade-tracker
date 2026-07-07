import httpx
from datetime import datetime, timezone
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.market import Market

logger = logging.getLogger(__name__)

KALSHI_API_URL = "https://external-api.kalshi.com/trade-api/v2"

async def fetch_active_markets(session: AsyncSession) -> None:
    """Fetch active markets from Kalshi API and upsert into DB."""
    async with httpx.AsyncClient() as client:
        url = f"{KALSHI_API_URL}/markets?status=open&limit=200"
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            markets = data.get("markets", [])
            for item in markets:
                external_id = item.get("ticker")
                if not external_id:
                    continue
                
                stmt = select(Market).where(
                    Market.platform == 'kalshi',
                    Market.external_market_id == external_id
                )
                result = await session.execute(stmt)
                market = result.scalar_one_or_none()
                
                open_time = item.get("open_time")
                close_time = item.get("close_time")
                
                if market is None:
                    market = Market(
                        platform='kalshi',
                        external_market_id=external_id,
                        title=item.get("title", ""), # We might need to fetch /events or /series for better titles
                        category=None,
                        open_date=datetime.fromisoformat(open_time.replace("Z", "+00:00")) if open_time else None,
                        resolution_date=datetime.fromisoformat(close_time.replace("Z", "+00:00")) if close_time else None,
                        resolved=False,
                        resolved_outcome=None
                    )
                    session.add(market)
            
            await session.commit()
            logger.info("Successfully fetched and updated active Kalshi markets.")
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            await session.rollback()

async def fetch_public_trades(session: AsyncSession, ticker: str) -> None:
    """Fetch public trades for a specific market ticker."""
    async with httpx.AsyncClient() as client:
        url = f"{KALSHI_API_URL}/markets/trades?ticker={ticker}&limit=100"
        try:
            response = await client.get(url)
            response.raise_for_status()
            # Process trades
            pass
        except Exception as e:
            logger.error(f"Error fetching Kalshi trades for {ticker}: {e}")
