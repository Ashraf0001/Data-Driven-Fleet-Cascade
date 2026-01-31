"""
Forecasting API routes.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException

from src.api.models.schemas import ForecastRequest, ForecastResponse
from src.data.loader import generate_demand_forecast
from src.forecasting.models.xgboost_model import DemandForecaster


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["forecasting"])

# Model cache
_model_cache: Dict[str, DemandForecaster] = {}


def get_forecaster(model_path: Optional[Path] = None) -> Optional[DemandForecaster]:
    """Get or load demand forecaster model."""
    if "demand" in _model_cache:
        return _model_cache["demand"]

    if model_path and model_path.exists():
        try:
            model = DemandForecaster.load(model_path)
            _model_cache["demand"] = model
            return model
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")

    return None


@router.post("/forecast", response_model=ForecastResponse)
async def forecast_demand(request: ForecastRequest) -> ForecastResponse:
    """
    Generate demand forecasts for specified zones.

    Uses trained XGBoost model if available, otherwise falls back
    to heuristic forecast.
    """
    try:
        # Try to load trained model
        model_path = Path("data/models/demand_forecast")
        forecaster = get_forecaster(model_path)

        if forecaster:
            # Use ML model
            forecasts = forecaster.predict_by_zone(
                hour=request.hour,
                day_of_week=request.day_of_week,
                month=request.month,
                zone_ids=request.zone_ids,
                historical_demand=request.historical_demand,
            )

            # Extend to horizon if needed
            result_forecasts = {
                str(zone_id): [forecasts[zone_id]] * request.horizon_hours
                for zone_id in request.zone_ids
            }

            return ForecastResponse(
                status="success",
                forecasts=result_forecasts,
                metadata={"model": "xgboost", "metrics": forecaster.metrics},
            )
        # Fall back to heuristic
        n_zones = max(request.zone_ids) + 1 if request.zone_ids else 25
        heuristic_demand = generate_demand_forecast(
            n_zones=n_zones, hour=request.hour, day_of_week=request.day_of_week
        )

        result_forecasts = {
            str(zone_id): [float(heuristic_demand[zone_id])] * request.horizon_hours
            for zone_id in request.zone_ids
            if zone_id < len(heuristic_demand)
        }

        return ForecastResponse(
            status="success", forecasts=result_forecasts, metadata={"model": "heuristic"}
        )

    except Exception as e:
        logger.error(f"Forecast failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/zones")
async def get_available_zones(n_zones: int = 25) -> Dict[str, Any]:
    """Get list of available zones for forecasting."""
    return {
        "zones": list(range(n_zones)),
        "grid_size": int(n_zones**0.5),
        "description": "Zone IDs are 0-indexed. Grid layout with (0,0) at top-left.",
    }
