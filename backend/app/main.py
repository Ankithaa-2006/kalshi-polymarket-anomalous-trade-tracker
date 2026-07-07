from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # We will initialize the scheduler here later
    yield
    # Shutdown
    # We will shutdown the scheduler here later
    pass

app = FastAPI(
    title="Prediction Market Anomaly Tracker",
    description="Research tool for detecting anomalous betting activity on Kalshi and Polymarket.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api")
