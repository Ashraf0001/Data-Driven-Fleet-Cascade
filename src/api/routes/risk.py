"""
Risk prediction API routes.
"""

import logging
from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.models.schemas import (
    RiskScoreRequest,
    RiskScoreResponse,
    VehicleRiskScore,
)
from src.risk.models.rul_model import calculate_heuristic_risk
from src.utils.config import get_config, get_config_value


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["risk"])


@router.post("/risk/score", response_model=RiskScoreResponse)
async def calculate_risk_scores(request: RiskScoreRequest) -> RiskScoreResponse:
    """
    Calculate risk scores for fleet vehicles.

    Uses heuristic scoring based on age, mileage, and status.
    ML-based scoring available when model is trained.
    """
    try:
        # Convert to DataFrame
        fleet_data = [
            {
                "vehicle_id": v.vehicle_id,
                "current_zone": v.current_zone,
                "status": v.status,
                "mileage_km": v.mileage_km or 50000,
                "age_months": v.age_months or 24,
            }
            for v in request.vehicles
        ]
        fleet_df = pd.DataFrame(fleet_data)

        # Calculate risk scores
        weights = get_config_value(
            get_config(), "risk.heuristic_weights", {"age": 0.3, "mileage": 0.4, "maintenance": 0.3}
        )
        result_df = calculate_heuristic_risk(fleet_df, weights=weights)

        # Build response
        risk_scores = []
        for _, row in result_df.iterrows():
            risk_scores.append(
                VehicleRiskScore(
                    vehicle_id=row["vehicle_id"],
                    risk_score=row["risk_score"],
                    risk_category=str(row["risk_category"]),
                    factors={
                        "age_contribution": row.get("age_months", 0) / 60 * weights["age"],
                        "mileage_contribution": row.get("mileage_km", 0)
                        / 100000
                        * weights["mileage"],
                        "status_contribution": weights["maintenance"]
                        if row["status"] == "maintenance"
                        else 0,
                    },
                )
            )

        # Summary
        summary = result_df["risk_category"].value_counts().to_dict()

        return RiskScoreResponse(
            status="success",
            risk_scores=risk_scores,
            summary={str(k): int(v) for k, v in summary.items()},
        )

    except Exception as e:
        logger.error(f"Risk scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/thresholds")
async def get_risk_thresholds() -> Dict[str, Any]:
    """Get risk categorization thresholds."""
    thresholds = get_config_value(
        get_config(), "risk.thresholds", {"high": 0.7, "medium": 0.4, "low": 0.0}
    )
    weights = get_config_value(
        get_config(), "risk.heuristic_weights", {"age": 0.3, "mileage": 0.4, "maintenance": 0.3}
    )
    return {
        "thresholds": {
            "high": {
                "min": thresholds["high"],
                "max": 1.0,
                "action": "Schedule immediate maintenance",
            },
            "medium": {
                "min": thresholds["medium"],
                "max": thresholds["high"],
                "action": "Monitor closely, plan maintenance",
            },
            "low": {
                "min": thresholds["low"],
                "max": thresholds["medium"],
                "action": "Normal operations",
            },
        },
        "factors": {
            "age": {"weight": weights["age"], "description": "Vehicle age in months"},
            "mileage": {"weight": weights["mileage"], "description": "Total kilometers driven"},
            "maintenance": {
                "weight": weights["maintenance"],
                "description": "Current maintenance status",
            },
        },
    }
