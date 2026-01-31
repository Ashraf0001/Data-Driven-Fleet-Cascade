"""
Cascading fleet optimization using OR-Tools.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from ortools.graph.python import min_cost_flow


logger = logging.getLogger(__name__)


@dataclass
class AllocationResult:
    """Result of fleet optimization."""

    status: str
    total_cost: float
    allocations: List[Dict[str, Any]]
    coverage: float
    kpis: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "total_cost": self.total_cost,
            "allocations": self.allocations,
            "coverage": self.coverage,
            "kpis": self.kpis,
        }


class FleetOptimizer:
    """
    Fleet allocation optimizer using min-cost flow.

    Network structure:
    - Source node: supplies all available vehicles
    - Vehicle nodes: one per operational vehicle
    - Zone nodes: one per service zone
    - Sink node: absorbs satisfied demand
    """

    def __init__(self, max_cost_per_vehicle: float = 50.0, min_service_level: float = 0.0):
        """
        Initialize fleet optimizer.

        Args:
            max_cost_per_vehicle: Maximum rebalancing cost per vehicle
            min_service_level: Minimum demand coverage (0-1)
        """
        self.max_cost_per_vehicle = max_cost_per_vehicle
        self.min_service_level = min_service_level

    def optimize(
        self,
        fleet_df: pd.DataFrame,
        demand: np.ndarray,
        costs: np.ndarray,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> AllocationResult:
        """
        Run min-cost flow optimization.

        Args:
            fleet_df: Fleet state DataFrame with columns:
                - vehicle_id: Unique identifier
                - current_zone: Current zone (int)
                - status: 'operational' or 'maintenance'
            demand: Demand per zone (1D array)
            costs: Zone-to-zone cost matrix (2D array)
            constraints: Optional constraint overrides

        Returns:
            AllocationResult with optimized allocations
        """
        logger.info("Running fleet optimization...")

        # Apply constraints
        max_cost = (
            constraints.get("max_cost_per_vehicle", self.max_cost_per_vehicle)
            if constraints
            else self.max_cost_per_vehicle
        )

        # Get operational vehicles
        op_fleet = fleet_df[fleet_df["status"] == "operational"].copy().reset_index(drop=True)
        n_vehicles = len(op_fleet)
        n_zones = len(demand)

        if n_vehicles == 0:
            logger.warning("No operational vehicles available")
            return AllocationResult(
                status="infeasible",
                total_cost=0,
                allocations=[],
                coverage=0,
                kpis={"vehicles_available": 0, "total_demand": int(demand.sum())},
            )

        # Node indices
        SOURCE = 0
        vehicle_nodes = list(range(1, n_vehicles + 1))
        zone_nodes = list(range(n_vehicles + 1, n_vehicles + 1 + n_zones))
        SINK = n_vehicles + 1 + n_zones

        # Create solver
        smcf = min_cost_flow.SimpleMinCostFlow()

        # Add arcs from source to each vehicle (capacity=1, cost=0)
        for v_node in vehicle_nodes:
            smcf.add_arc_with_capacity_and_unit_cost(SOURCE, v_node, 1, 0)

        # Add arcs from each vehicle to each zone
        vehicle_zones = op_fleet["current_zone"].values
        for i, (v_node, v_zone) in enumerate(zip(vehicle_nodes, vehicle_zones)):
            for j, z_node in enumerate(zone_nodes):
                travel_cost = int(costs[v_zone, j] * 100)  # Scale to int
                if travel_cost < max_cost * 100:
                    smcf.add_arc_with_capacity_and_unit_cost(v_node, z_node, 1, travel_cost)

        # Add arcs from zones to sink
        for j, z_node in enumerate(zone_nodes):
            zone_demand = min(int(demand[j]), n_vehicles)
            smcf.add_arc_with_capacity_and_unit_cost(z_node, SINK, zone_demand, 0)

        # Set supplies
        total_supply = n_vehicles
        total_demand = min(int(demand.sum()), n_vehicles)

        smcf.set_node_supply(SOURCE, total_supply)
        smcf.set_node_supply(SINK, -total_demand)

        # Solve
        status = smcf.solve()

        if status != smcf.OPTIMAL:
            logger.warning(f"Optimization status: {status}")
            return AllocationResult(
                status="infeasible",
                total_cost=0,
                allocations=[],
                coverage=0,
                kpis={"solver_status": status},
            )

        # Extract results
        total_cost = smcf.optimal_cost() / 100
        allocations = []

        for arc in range(smcf.num_arcs()):
            if smcf.flow(arc) > 0:
                tail = smcf.tail(arc)
                head = smcf.head(arc)

                if tail in vehicle_nodes and head in zone_nodes:
                    v_idx = tail - 1
                    z_idx = head - n_vehicles - 1
                    from_zone = int(vehicle_zones[v_idx])

                    allocations.append(
                        {
                            "vehicle_id": op_fleet.iloc[v_idx]["vehicle_id"],
                            "from_zone": from_zone,
                            "to_zone": z_idx,
                            "cost": float(costs[from_zone, z_idx]),
                            "rebalanced": from_zone != z_idx,
                        }
                    )

        # Calculate KPIs
        zones_served = len(set(a["to_zone"] for a in allocations))
        rebalanced_count = sum(1 for a in allocations if a["rebalanced"])
        coverage = zones_served / n_zones if n_zones > 0 else 0

        kpis = {
            "vehicles_allocated": len(allocations),
            "vehicles_rebalanced": rebalanced_count,
            "zones_served": zones_served,
            "total_zones": n_zones,
            "total_demand": int(demand.sum()),
            "demand_served": len(allocations),
            "utilization": len(allocations) / n_vehicles if n_vehicles > 0 else 0,
        }

        logger.info(
            f"Optimization complete: {len(allocations)} allocations, cost=${total_cost:.2f}"
        )

        return AllocationResult(
            status="optimal",
            total_cost=total_cost,
            allocations=allocations,
            coverage=coverage,
            kpis=kpis,
        )

    def optimize_multi_period(
        self,
        fleet_df: pd.DataFrame,
        demand_forecast: Dict[int, np.ndarray],
        costs: np.ndarray,
        periods: int = 24,
    ) -> List[AllocationResult]:
        """
        Run optimization for multiple time periods.

        Args:
            fleet_df: Initial fleet state
            demand_forecast: Dictionary of period -> demand array
            costs: Zone-to-zone cost matrix
            periods: Number of periods to optimize

        Returns:
            List of AllocationResult per period
        """
        results = []
        current_fleet = fleet_df.copy()

        for period in range(periods):
            if period not in demand_forecast:
                continue

            demand = demand_forecast[period]
            result = self.optimize(current_fleet, demand, costs)
            results.append(result)

            # Update fleet positions for next period
            if result.status == "optimal":
                for alloc in result.allocations:
                    mask = current_fleet["vehicle_id"] == alloc["vehicle_id"]
                    current_fleet.loc[mask, "current_zone"] = alloc["to_zone"]

        return results
