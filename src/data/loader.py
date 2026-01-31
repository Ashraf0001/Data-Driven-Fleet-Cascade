"""
Data loading utilities for Fleet Decision Platform.

Handles loading of:
- Uber/taxi ride data for demand forecasting
- NASA Turbofan data for risk prediction
- Fleet state data
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# NASA C-MAPSS column definitions
SENSOR_COLUMNS = [f"sensor_{i}" for i in range(1, 22)]
OP_COLUMNS = [f"op_setting_{i}" for i in range(1, 4)]
TURBOFAN_COLUMNS = ["unit_id", "time_cycles"] + OP_COLUMNS + SENSOR_COLUMNS


def load_uber_data(path: Path | str) -> pd.DataFrame:
    """
    Load Uber/taxi ride data.

    Args:
        path: Path to CSV file

    Returns:
        DataFrame with ride data
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Uber data not found at {path}")

    logger.info(f"Loading Uber data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df):,} records")

    return df


def load_nasa_turbofan(
    data_dir: Path | str,
    dataset: str = "FD001"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load NASA C-MAPSS turbofan dataset.

    Args:
        data_dir: Directory containing CMaps data
        dataset: Dataset subset (FD001, FD002, FD003, FD004)

    Returns:
        Tuple of (train_df, rul_df)
    """
    data_dir = Path(data_dir)
    train_path = data_dir / f"train_{dataset}.txt"
    rul_path = data_dir / f"RUL_{dataset}.txt"

    if not train_path.exists():
        raise FileNotFoundError(f"Training data not found at {train_path}")

    logger.info(f"Loading NASA Turbofan {dataset} from {data_dir}")

    # Load training data
    train_df = pd.read_csv(
        train_path,
        sep=r"\s+",
        header=None,
        names=TURBOFAN_COLUMNS
    )

    # Load RUL labels
    rul_df = pd.read_csv(rul_path, header=None, names=["RUL"])

    logger.info(f"Loaded {len(train_df):,} sensor readings from {train_df['unit_id'].nunique()} engines")

    return train_df, rul_df


def load_fleet_state(path: Optional[Path | str] = None) -> pd.DataFrame:
    """
    Load fleet state from file or generate default.

    Args:
        path: Optional path to fleet state parquet file

    Returns:
        DataFrame with fleet state
    """
    if path and Path(path).exists():
        logger.info(f"Loading fleet state from {path}")
        return pd.read_parquet(path)

    logger.warning("No fleet state file found, use generate_fleet_state() to create one")
    return pd.DataFrame()


def generate_fleet_state(
    n_vehicles: int = 50,
    n_zones: int = 25,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate simulated fleet state.

    Args:
        n_vehicles: Number of vehicles
        n_zones: Number of service zones
        seed: Random seed

    Returns:
        DataFrame with fleet state
    """
    np.random.seed(seed)

    fleet = pd.DataFrame({
        "vehicle_id": [f"V{i:03d}" for i in range(1, n_vehicles + 1)],
        "current_zone": np.random.randint(0, n_zones, n_vehicles),
        "capacity": np.ones(n_vehicles, dtype=int),
        "status": np.random.choice(
            ["operational", "operational", "operational", "maintenance"],
            n_vehicles
        ),
        "mileage_km": np.random.randint(10000, 100000, n_vehicles),
        "age_months": np.random.randint(6, 60, n_vehicles),
        "risk_score": np.random.uniform(0.1, 0.9, n_vehicles).round(3),
    })

    logger.info(f"Generated fleet state: {n_vehicles} vehicles, {n_zones} zones")
    return fleet


def generate_network_costs(n_zones: int = 25, seed: int = 42) -> np.ndarray:
    """
    Generate zone-to-zone travel cost matrix.

    Args:
        n_zones: Number of zones
        seed: Random seed

    Returns:
        2D numpy array of costs
    """
    np.random.seed(seed)

    # Create grid positions
    grid_size = int(np.sqrt(n_zones))
    positions = [(i // grid_size, i % grid_size) for i in range(n_zones)]

    # Calculate Euclidean distances and scale to costs
    costs = np.zeros((n_zones, n_zones))
    for i in range(n_zones):
        for j in range(n_zones):
            dist = np.sqrt(
                (positions[i][0] - positions[j][0]) ** 2 +
                (positions[i][1] - positions[j][1]) ** 2
            )
            # Cost = distance * base_rate + random_factor
            costs[i, j] = dist * 5 + np.random.uniform(0, 2)

    logger.info(f"Generated {n_zones}x{n_zones} network cost matrix")
    return costs


def generate_demand_forecast(
    n_zones: int = 25,
    hour: int = 18,
    day_of_week: int = 4,
    seed: int = 42
) -> np.ndarray:
    """
    Generate demand forecast per zone.

    Args:
        n_zones: Number of zones
        hour: Hour of day (0-23)
        day_of_week: Day of week (0=Mon, 6=Sun)
        seed: Random seed

    Returns:
        1D numpy array of demand per zone
    """
    np.random.seed(seed)

    grid_size = int(np.sqrt(n_zones))
    base_demand = np.zeros(n_zones)

    for z in range(n_zones):
        row, col = z // grid_size, z % grid_size
        center_dist = np.sqrt((row - grid_size / 2) ** 2 + (col - grid_size / 2) ** 2)
        base_demand[z] = max(5, 15 - center_dist * 2) + np.random.randint(0, 5)

    # Time adjustments
    if 17 <= hour <= 19:
        time_multiplier = 1.5
    elif 7 <= hour <= 9:
        time_multiplier = 1.3
    else:
        time_multiplier = 1.0

    if day_of_week >= 5:
        time_multiplier *= 0.8

    return (base_demand * time_multiplier).astype(int)
