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
        result_df = calculate_heuristic_risk(fleet_df)

        # Build response
        risk_scores = []
        for _, row in result_df.iterrows():
            risk_scores.append(
                VehicleRiskScore(
                    vehicle_id=row["vehicle_id"],
                    risk_score=row["risk_score"],
                    risk_category=str(row["risk_category"]),
                    factors={
                        "age_contribution": row.get("age_months", 0) / 60 * 0.3,
                        "mileage_contribution": row.get("mileage_km", 0) / 100000 * 0.4,
                        "status_contribution": 0.3 if row["status"] == "maintenance" else 0,
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
    return {
        "thresholds": {
            "high": {"min": 0.7, "max": 1.0, "action": "Schedule immediate maintenance"},
            "medium": {"min": 0.4, "max": 0.7, "action": "Monitor closely, plan maintenance"},
            "low": {"min": 0.0, "max": 0.4, "action": "Normal operations"},
        },
        "factors": {
            "age": {"weight": 0.3, "description": "Vehicle age in months"},
            "mileage": {"weight": 0.4, "description": "Total kilometers driven"},
            "maintenance": {"weight": 0.3, "description": "Current maintenance status"},
        },
    }
