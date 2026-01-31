"""
Fleet Decision Platform - FastAPI Application.

Enterprise-grade decision intelligence platform for fleet operations.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.models.schemas import ConfigResponse, HealthResponse
from src.api.routes import forecast, optimize, risk


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Fleet Decision Platform starting...")
    logger.info("📊 Loading models and configuration...")

    # TODO: Load models here if needed
    # demand_model = DemandForecaster.load("data/models/demand_forecast")

    yield

    # Shutdown
    logger.info("👋 Fleet Decision Platform shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Fleet Decision Platform",
    description="""
## Enterprise-grade Decision Intelligence for Fleet Operations

### Capabilities

- **Demand Forecasting**: Predict ride demand per zone using XGBoost
- **Fleet Optimization**: Allocate vehicles using min-cost flow
- **Risk Prediction**: Assess vehicle health and failure risk
- **Explainability**: Understand model decisions

### Quick Start

1. Check health: `GET /health`
2. Run optimization: `POST /api/v1/optimize`
3. Get forecasts: `POST /api/v1/forecast`
4. Calculate risk: `POST /api/v1/risk/score`

### Documentation

- [Interactive API Docs](/docs)
- [ReDoc](/redoc)
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(optimize.router)
app.include_router(forecast.router)
app.include_router(risk.router)


# ==============================================================================
# Root Endpoints
# ==============================================================================


@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "Fleet Decision Platform",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "optimize": "/api/v1/optimize",
            "forecast": "/api/v1/forecast",
            "risk": "/api/v1/risk/score",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/api/v1/config", response_model=ConfigResponse, tags=["configuration"])
async def get_config() -> ConfigResponse:
    """Get current platform configuration."""
    return ConfigResponse(
        forecasting={
            "model": "xgboost",
            "horizon_days": 7,
            "features": ["hour", "day_of_week", "month", "is_weekend", "zone_id"],
        },
        optimization={
            "solver": "ortools",
            "stages": ["min_cost_flow"],
            "max_cost_per_vehicle": 50.0,
        },
        risk={"model": "heuristic", "thresholds": {"high": 0.7, "medium": 0.4, "low": 0.0}},
    )


# ==============================================================================
# Run Server
# ==============================================================================


def run():
    """Run the API server."""
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
