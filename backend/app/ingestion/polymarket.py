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
            for trade in data:
                # We need to map trade to market and bet
                market_id_ext = trade.get('condition_id')
                if not market_id_ext:
                    continue
                
                stmt = select(Market).where(Market.external_market_id == market_id_ext, Market.platform == 'polymarket')
                res = await session.execute(stmt)
                market = res.scalar_one_or_none()
                if not market:
                    continue

                # Ensure Trader exists
                stmt_tr = select(Trader).where(Trader.external_trader_id == wallet_address, Trader.platform == 'polymarket')
                res_tr = await session.execute(stmt_tr)
                trader = res_tr.scalar_one_or_none()
                if not trader:
                    trader = Trader(platform='polymarket', external_trader_id=wallet_address)
                    session.add(trader)
                    await session.flush()

                trade_time_str = trade.get('timestamp')
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

                # Check if bet exists
                # Polymarket trades might not have a unique ID in the simplified API, but let's assume they do
                # or just insert since this is append-only. We'll use a unique compound check or just skip duplicates if they have transaction_hash.
                tx_hash = trade.get('transaction_hash', '')
                
                # We'll just insert for now as a mock logic
                bet = Bet(
                    market_id=market.id,
                    trader_id=trader.id,
                    side='yes' if trade.get('outcome') == 'Yes' else 'no',
                    size=float(trade.get('size', 0)),
                    price=float(trade.get('price', 0)),
                    bet_timestamp=trade_time,
                    time_to_resolution_hours=time_to_res
                )
                session.add(bet)

            await session.commit()
            logger.info(f"Successfully fetched trades for {wallet_address}.")
        except Exception as e:
            logger.error(f"Error fetching trades for {wallet_address}: {e}")
            await session.rollback()
