import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Coroutine, Any

from .database import async_session_maker
from .ingestion import polymarket, kalshi

logger = logging.getLogger(__name__)

async def run_job(job_func: Callable[[AsyncSession], Coroutine[Any, Any, None]]):
    """Wrapper to inject a DB session into scheduled jobs."""
    async with async_session_maker() as session:
        try:
            await job_func(session)
        except Exception as e:
            logger.error(f"Error in background job {job_func.__name__}: {e}")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    
    # Polymarket Ingestion
    scheduler.add_job(
        run_job,
        'interval',
        minutes=15,
        args=[polymarket.fetch_active_markets],
        id='poly_active_markets',
        replace_existing=True
    )
    
    # Kalshi Ingestion
    scheduler.add_job(
        run_job,
        'interval',
        minutes=15,
        args=[kalshi.fetch_active_markets],
        id='kalshi_active_markets',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started.")
    return scheduler
