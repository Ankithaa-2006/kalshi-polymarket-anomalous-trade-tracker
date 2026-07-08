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
            trades = data.get("trades", [])
            for trade in trades:
                # We need to map trade to market and bet
                stmt = select(Market).where(Market.external_market_id == ticker, Market.platform == 'kalshi')
                res = await session.execute(stmt)
                market = res.scalar_one_or_none()
                if not market:
                    continue

                trade_time_str = trade.get('created_time')
                if trade_time_str:
                    try:
                        trade_time = datetime.fromisoformat(trade_time_str.replace("Z", "+00:00"))
                    except:
                        trade_time = datetime.now(timezone.utc)
                else:
                    trade_time = datetime.now(timezone.utc)

                time_to_res = None
                if market.resolution_date:
                    delta = market.resolution_date - trade_time
                    time_to_res = max(0, delta.total_seconds() / 3600.0)

                # Kalshi public trades don't reveal trader ID directly, so we use None
                bet = Bet(
                    market_id=market.id,
                    trader_id=None,
                    side='yes' if trade.get('yes_price', 0) > trade.get('no_price', 0) else 'no',
                    size=float(trade.get('count', 0)),
                    price=float(trade.get('yes_price', 0)) / 100.0 if trade.get('yes_price') else 0.5,
                    bet_timestamp=trade_time,
                    time_to_resolution_hours=time_to_res
                )
                session.add(bet)

            await session.commit()
            logger.info(f"Successfully fetched Kalshi trades for {ticker}.")
        except Exception as e:
            logger.error(f"Error fetching Kalshi trades for {ticker}: {e}")
            await session.rollback()
