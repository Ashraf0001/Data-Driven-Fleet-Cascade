"""
Optimization API routes.
"""

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.models.schemas import (
    Allocation,
    OptimizationKPIs,
    OptimizationRequest,
    OptimizationResponse,
)
from src.data.loader import generate_network_costs
from src.optimization.cascade import FleetOptimizer


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["optimization"])


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_fleet(request: OptimizationRequest) -> OptimizationResponse:
    """
    Run fleet optimization to allocate vehicles to zones.

    Given demand forecasts per zone and current fleet state,
    computes optimal vehicle allocations using min-cost flow.
    """
    try:
        # Convert fleet state to DataFrame
        fleet_data = [
            {
                "vehicle_id": v.vehicle_id,
                "current_zone": v.current_zone,
                "capacity": v.capacity,
                "status": v.status,
                "mileage_km": v.mileage_km or 50000,
                "age_months": v.age_months or 24,
                "risk_score": v.risk_score or 0.5,
            }
            for v in request.fleet_state.vehicles
        ]
        fleet_df = pd.DataFrame(fleet_data)

        # Convert demand forecast
        # For simplicity, use the first value from each zone's forecast
        zone_ids = sorted([int(k) for k in request.demand_forecast.keys()])
        n_zones = max(zone_ids) + 1 if zone_ids else 1

        demand = np.zeros(n_zones)
        for zone_id, values in request.demand_forecast.items():
            z = int(zone_id)
            if z < n_zones:
                demand[z] = values[0] if values else 0

        # Get or generate network costs
        if request.network_costs:
            costs = np.array(request.network_costs)
        else:
            costs = generate_network_costs(n_zones)

        # Run optimization
        optimizer = FleetOptimizer(
            max_cost_per_vehicle=request.constraints.max_cost_per_vehicle,
            min_service_level=request.constraints.min_service_level,
        )

        result = optimizer.optimize(
            fleet_df=fleet_df,
            demand=demand,
            costs=costs,
            constraints=request.constraints.model_dump(),
        )

        # Convert to response
        allocations = [
            Allocation(
                vehicle_id=a["vehicle_id"],
                from_zone=a["from_zone"],
                to_zone=a["to_zone"],
                cost=a["cost"],
                rebalanced=a.get("rebalanced", False),
            )
            for a in result.allocations
        ]

        kpis = OptimizationKPIs(**result.kpis)

        return OptimizationResponse(
            status=result.status,
            total_cost=result.total_cost,
            allocations=allocations,
            coverage=result.coverage,
            kpis=kpis,
        )

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/simulate")
async def simulate_optimization(
    n_vehicles: int = 50, n_zones: int = 25, hour: int = 18, day_of_week: int = 4
) -> Dict[str, Any]:
    """
    Run optimization with simulated data for testing.

    Generates synthetic fleet state and demand, then runs optimization.
    """
    from src.data.loader import (
        generate_demand_forecast,
        generate_fleet_state,
        generate_network_costs,
    )

    try:
        # Generate data
        fleet_df = generate_fleet_state(n_vehicles, n_zones)
        demand = generate_demand_forecast(n_zones, hour, day_of_week)
        costs = generate_network_costs(n_zones)

        # Run optimization
        optimizer = FleetOptimizer()
        result = optimizer.optimize(fleet_df, demand, costs)

        return {
            "status": result.status,
            "total_cost": result.total_cost,
            "num_allocations": len(result.allocations),
            "coverage": result.coverage,
            "kpis": result.kpis,
            "sample_allocations": result.allocations[:5],
        }

    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
