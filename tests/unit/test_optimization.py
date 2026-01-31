"""
Unit tests for fleet optimization.
"""

import numpy as np
import pandas as pd
import pytest

from src.optimization.cascade import FleetOptimizer


@pytest.fixture
def sample_fleet():
    """Create sample fleet DataFrame."""
    return pd.DataFrame(
        {
            "vehicle_id": ["V001", "V002", "V003", "V004", "V005"],
            "current_zone": [0, 1, 2, 3, 4],
            "capacity": [1, 1, 1, 1, 1],
            "status": ["operational", "operational", "operational", "maintenance", "operational"],
        }
    )


@pytest.fixture
def sample_costs():
    """Create sample cost matrix (5x5)."""
    return np.array(
        [
            [0, 5, 10, 15, 20],
            [5, 0, 5, 10, 15],
            [10, 5, 0, 5, 10],
            [15, 10, 5, 0, 5],
            [20, 15, 10, 5, 0],
        ],
        dtype=float,
    )


@pytest.fixture
def sample_demand():
    """Create sample demand."""
    return np.array([3, 2, 4, 1, 2])


class TestFleetOptimizer:
    """Tests for FleetOptimizer class."""

    def test_optimizer_init(self):
        """Test optimizer initialization."""
        optimizer = FleetOptimizer(max_cost_per_vehicle=100)
        assert optimizer.max_cost_per_vehicle == 100

    def test_optimize_basic(self, sample_fleet, sample_costs, sample_demand):
        """Test basic optimization."""
        optimizer = FleetOptimizer()
        result = optimizer.optimize(sample_fleet, sample_demand, sample_costs)

        assert result.status == "optimal"
        assert result.total_cost >= 0
        assert len(result.allocations) > 0

    def test_optimize_no_operational_vehicles(self, sample_costs, sample_demand):
        """Test with no operational vehicles."""
        fleet = pd.DataFrame(
            {
                "vehicle_id": ["V001"],
                "current_zone": [0],
                "status": ["maintenance"],
            }
        )

        optimizer = FleetOptimizer()
        result = optimizer.optimize(fleet, sample_demand, sample_costs)

        assert result.status == "infeasible"
        assert len(result.allocations) == 0

    def test_optimize_allocation_structure(self, sample_fleet, sample_costs, sample_demand):
        """Test allocation result structure."""
        optimizer = FleetOptimizer()
        result = optimizer.optimize(sample_fleet, sample_demand, sample_costs)

        for alloc in result.allocations:
            assert "vehicle_id" in alloc
            assert "from_zone" in alloc
            assert "to_zone" in alloc
            assert "cost" in alloc

    def test_optimize_kpis(self, sample_fleet, sample_costs, sample_demand):
        """Test KPIs are calculated."""
        optimizer = FleetOptimizer()
        result = optimizer.optimize(sample_fleet, sample_demand, sample_costs)

        assert "vehicles_allocated" in result.kpis
        assert "zones_served" in result.kpis
        assert "total_demand" in result.kpis
