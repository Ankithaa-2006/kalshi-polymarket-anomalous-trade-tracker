import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Coroutine, Any

from .database import async_session_maker
from .ingestion import polymarket, kalshi
from .scoring import matching, reputation, calibration

logger = logging.getLogger(__name__)

async def run_job(job_func: Callable[[AsyncSession], Coroutine[Any, Any, None]]):
    """Wrapper to inject a DB session into scheduled jobs."""
    async with async_session_maker() as session:
        try:
            await job_func(session)
        except Exception as e:
            logger.error(f"Error in background job {job_func.__name__}: {e}")

async def run_job_no_args(job_func: Callable[[], Coroutine[Any, Any, None]]):
    """Wrapper for jobs that don't need a session injected."""
    try:
        await job_func()
    except Exception as e:
        logger.error(f"Error in background job {job_func.__name__}: {e}")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    
    # Ingestion Jobs (every 15 min)
    scheduler.add_job(run_job, 'interval', minutes=15, args=[polymarket.fetch_active_markets], id='poly_active_markets', replace_existing=True)
    scheduler.add_job(run_job, 'interval', minutes=15, args=[kalshi.fetch_active_markets], id='kalshi_active_markets', replace_existing=True)
    
    # V2 Daily Jobs
    scheduler.add_job(run_job_no_args, 'interval', hours=24, args=[matching.compute_market_matches], id='market_matches', replace_existing=True)
    scheduler.add_job(run_job_no_args, 'interval', hours=24, args=[reputation.compute_reputations], id='compute_reputations', replace_existing=True)
    scheduler.add_job(run_job_no_args, 'interval', hours=24, args=[calibration.update_calibration_summary], id='calibration_summary', replace_existing=True)
    
    scheduler.start()
    logger.info("APScheduler started with v2 jobs.")
    return scheduler
