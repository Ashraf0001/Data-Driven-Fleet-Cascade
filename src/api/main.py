"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.utils.config import load_config
from src.utils.logging import get_logger, setup_logging


# Load configuration
config = load_config()

# Setup logging
setup_logging(
    level=config.get("logging", {}).get("level", "INFO"),
    format=config.get("logging", {}).get("format", "text"),
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Fleet Decision Platform API")
    logger.info(f"Debug mode: {config.get('api', {}).get('debug', False)}")
    yield
    # Shutdown
    logger.info("Shutting down Fleet Decision Platform API")


# Create FastAPI application
app = FastAPI(
    title="Fleet Decision Platform",
    description="Enterprise-grade decision intelligence platform for fleet operations",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
cors_config = config.get("api", {}).get("cors", {})
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allow_origins", ["*"]),
    allow_credentials=True,
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
)


# =============================================================================
# Health Check Endpoints
# =============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Fleet Decision Platform",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


# =============================================================================
# API Routes (to be implemented)
# =============================================================================


@app.get("/api/v1/config", tags=["Configuration"])
async def get_configuration() -> dict[str, Any]:
    """Get current configuration (non-sensitive values only)."""
    return {
        "forecasting": {
            "model": config.get("forecasting", {}).get("model"),
            "horizon_days": config.get("forecasting", {}).get("horizon_days"),
        },
        "optimization": {
            "solver": config.get("optimization", {}).get("solver"),
            "stages": config.get("optimization", {}).get("stages"),
        },
        "features": config.get("features", {}),
    }


# =============================================================================
# CLI Runner
# =============================================================================


def run():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=config.get("api", {}).get("host", "0.0.0.0"),
        port=config.get("api", {}).get("port", 8000),
        reload=config.get("api", {}).get("reload", True),
    )


if __name__ == "__main__":
    run()
