"""
Pydantic models for API request/response validation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ==============================================================================
# Common Models
# ==============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    """Error response."""

    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None


# ==============================================================================
# Fleet Models
# ==============================================================================


class Vehicle(BaseModel):
    """Vehicle state."""

    vehicle_id: str
    current_zone: int = Field(ge=0)
    capacity: int = Field(default=1, ge=1)
    status: str = Field(default="operational")
    mileage_km: Optional[float] = None
    age_months: Optional[int] = None
    risk_score: Optional[float] = Field(default=None, ge=0, le=1)


class FleetState(BaseModel):
    """Fleet state for optimization."""

    vehicles: List[Vehicle]


# ==============================================================================
# Optimization Models
# ==============================================================================


class OptimizationConstraints(BaseModel):
    """Constraints for optimization."""

    max_cost_per_vehicle: float = Field(default=50.0, ge=0)
    min_service_level: float = Field(default=0.0, ge=0, le=1)
    max_distance: Optional[float] = None


class OptimizationRequest(BaseModel):
    """Request body for fleet optimization."""

    demand_forecast: Dict[str, List[float]] = Field(
        ..., description="Demand per zone. Keys are zone IDs, values are demand arrays."
    )
    fleet_state: FleetState
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints)
    network_costs: Optional[List[List[float]]] = Field(
        default=None, description="Optional zone-to-zone cost matrix"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "demand_forecast": {"0": [10], "1": [15], "2": [8]},
                    "fleet_state": {
                        "vehicles": [
                            {"vehicle_id": "V001", "current_zone": 0},
                            {"vehicle_id": "V002", "current_zone": 1},
                        ]
                    },
                    "constraints": {"max_cost_per_vehicle": 50},
                }
            ]
        }
    }


class Allocation(BaseModel):
    """Single vehicle allocation."""

    vehicle_id: str
    from_zone: int
    to_zone: int
    cost: float
    rebalanced: bool = False


class OptimizationKPIs(BaseModel):
    """Key performance indicators."""

    vehicles_allocated: int = 0
    vehicles_rebalanced: int = 0
    zones_served: int = 0
    total_zones: int = 0
    total_demand: int = 0
    demand_served: int = 0
    utilization: float = 0.0


class OptimizationResponse(BaseModel):
    """Response from fleet optimization."""

    status: str
    total_cost: float
    allocations: List[Allocation]
    coverage: float = Field(ge=0, le=1)
    kpis: OptimizationKPIs

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "optimal",
                    "total_cost": 125.50,
                    "allocations": [
                        {
                            "vehicle_id": "V001",
                            "from_zone": 0,
                            "to_zone": 2,
                            "cost": 15.5,
                            "rebalanced": True,
                        }
                    ],
                    "coverage": 0.8,
                    "kpis": {
                        "vehicles_allocated": 10,
                        "vehicles_rebalanced": 3,
                        "zones_served": 8,
                        "total_zones": 10,
                        "total_demand": 50,
                        "demand_served": 10,
                        "utilization": 0.75,
                    },
                }
            ]
        }
    }


# ==============================================================================
# Forecasting Models
# ==============================================================================


class ForecastRequest(BaseModel):
    """Request for demand forecast."""

    zone_ids: List[int] = Field(default_factory=list)
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)
    horizon_hours: int = Field(default=1, ge=1, le=168)
    historical_demand: Optional[Dict[int, float]] = None


class ForecastResponse(BaseModel):
    """Response with demand forecasts."""

    status: str = "success"
    forecasts: Dict[str, List[float]] = Field(description="Predicted demand per zone")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# Risk Models
# ==============================================================================


class RiskScoreRequest(BaseModel):
    """Request for risk scoring."""

    vehicles: List[Vehicle]
    use_ml_model: bool = Field(default=False)


class VehicleRiskScore(BaseModel):
    """Risk score for a vehicle."""

    vehicle_id: str
    risk_score: float = Field(ge=0, le=1)
    risk_category: str
    factors: Optional[Dict[str, float]] = None


class RiskScoreResponse(BaseModel):
    """Response with risk scores."""

    status: str = "success"
    risk_scores: List[VehicleRiskScore]
    summary: Dict[str, int] = Field(default_factory=dict, description="Count per risk category")


# ==============================================================================
# Configuration Models
# ==============================================================================


class ConfigResponse(BaseModel):
    """Configuration response."""

    forecasting: Dict[str, Any]
    optimization: Dict[str, Any]
    risk: Dict[str, Any]
