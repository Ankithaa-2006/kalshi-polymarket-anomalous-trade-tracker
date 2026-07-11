from fastapi import APIRouter

from .bets import router as bets_router
from .traders import router as traders_router
from .markets import router as markets_router
from .calibration import router as calibration_router
from .watchlists import router as watchlists_router

api_router = APIRouter()

api_router.include_router(bets_router, prefix="/bets", tags=["bets"])
api_router.include_router(traders_router, prefix="/traders", tags=["traders"])
api_router.include_router(markets_router, prefix="/markets", tags=["markets"])
api_router.include_router(calibration_router, prefix="/calibration", tags=["calibration"])
api_router.include_router(watchlists_router, prefix="/watchlists", tags=["watchlists"])
