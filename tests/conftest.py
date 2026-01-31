"""Pytest fixtures for testing."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "data": {
            "nyc_taxi": {
                "zones": [1, 2, 3],
                "time_range": "2023-01-01:2023-01-31",
            },
            "fleet": {
                "num_vehicles": 10,
                "locations": 3,
                "simulation_seed": 42,
            },
        },
        "forecasting": {
            "model": "xgboost",
            "horizon_days": 7,
            "features": ["hour", "day_of_week", "month"],
        },
        "optimization": {
            "solver": "ortools",
            "stages": ["min_cost_flow"],
            "constraints": {
                "max_distance": 50,
                "capacity_per_vehicle": 1,
            },
        },
    }


@pytest.fixture
def sample_demand_data():
    """Sample demand data for testing."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=24 * 7, freq="H")
    locations = [1, 2, 3]

    data = []
    for location in locations:
        for date in dates:
            data.append(
                {
                    "location_id": location,
                    "timestamp": date,
                    "demand": np.random.poisson(10 + location * 2),
                }
            )

    return pd.DataFrame(data)


@pytest.fixture
def sample_fleet_state():
    """Sample fleet state for testing."""
    return pd.DataFrame(
        {
            "vehicle_id": [f"V{i:03d}" for i in range(10)],
            "location_id": [1, 1, 1, 2, 2, 2, 3, 3, 3, 3],
            "capacity": [1] * 10,
            "status": ["operational"] * 10,
        }
    )


@pytest.fixture
def sample_network_costs():
    """Sample network cost matrix for testing."""
    # 3 locations, zone-to-zone costs
    return np.array(
        [
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0],
        ]
    )


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory structure."""
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed").mkdir()
    (tmp_path / "models").mkdir()
    (tmp_path / "outputs").mkdir()
    return tmp_path
