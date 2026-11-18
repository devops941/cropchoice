import sys
from pathlib import Path

# Add backend directory to sys.path so direct imports work regardless of execution cwd
_backend_dir = Path(__file__).resolve().parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))
_root_dir = _backend_dir.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from db.mongo import ping, ensure_indexes, close_client
from routers import (
    auth, dashboard, crops, prices, farms,
    criteria, rankings, optimizer, scenarios,
    simulations, import_export, admin, reports
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure mongo indexes
    try:
        ensure_indexes()
    except Exception as e:
        print(f"Index initialization warning: {e}")
    yield
    # Shutdown
    close_client()


app = FastAPI(
    title="CropChoice API",
    description="Intelligent Crop Portfolio Ranking & Diversification Optimizer Engine",
    version="2.0.26",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.cors_origin_list + [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(crops.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(farms.router, prefix="/api")
app.include_router(criteria.router, prefix="/api")
app.include_router(rankings.router, prefix="/api")
app.include_router(optimizer.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")
app.include_router(import_export.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    db_ok = ping()
    return {
        "status": "healthy" if db_ok else "database_degraded",
        "app_env": settings.APP_ENV,
        "database_connected": db_ok,
        "version": "2.0.26"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "CropChoice API Engine",
        "docs": "/docs",
        "health": "/api/health"
    }
