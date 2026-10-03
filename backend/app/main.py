import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import endpoints, ingest, events, replay
from app.services.retry_worker import run_retry_worker_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch retry worker background loop
    worker_task = asyncio.create_task(run_retry_worker_loop())
    yield
    # Shutdown: cancel retry worker
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(endpoints.router)
app.include_router(ingest.router)
app.include_router(events.router)
app.include_router(replay.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }

