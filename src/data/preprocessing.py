"""
Data preprocessing and feature engineering for Fleet Decision Platform.
"""

import logging
from typing import List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def preprocess_uber_data(
    df: pd.DataFrame,
    n_zones: int = 5
) -> pd.DataFrame:
    """
    Clean and preprocess Uber/taxi data.

    Args:
        df: Raw Uber DataFrame
        n_zones: Number of zones per dimension (creates n_zones^2 total zones)

    Returns:
        Cleaned DataFrame with features
    """
    logger.info("Preprocessing Uber data...")
    clean_df = df.copy()

    # Drop missing values in key columns
    required_cols = ["pickup_datetime", "fare_amount", "pickup_longitude", "pickup_latitude"]
    for col in required_cols:
        if col in clean_df.columns:
            clean_df = clean_df.dropna(subset=[col])

    # Parse datetime
    clean_df["pickup_datetime"] = pd.to_datetime(clean_df["pickup_datetime"], errors="coerce")
    clean_df = clean_df.dropna(subset=["pickup_datetime"])

    # Extract time features
    clean_df["hour"] = clean_df["pickup_datetime"].dt.hour
    clean_df["day_of_week"] = clean_df["pickup_datetime"].dt.dayofweek
    clean_df["month"] = clean_df["pickup_datetime"].dt.month
    clean_df["year"] = clean_df["pickup_datetime"].dt.year
    clean_df["is_weekend"] = clean_df["day_of_week"].isin([5, 6]).astype(int)

    # Filter reasonable values
    clean_df = clean_df[
        (clean_df["fare_amount"] > 0) &
        (clean_df["fare_amount"] < 500) &
        (clean_df["pickup_longitude"].between(-75, -73)) &
        (clean_df["pickup_latitude"].between(40, 42))
    ]

    # Create zones
    clean_df["zone_id"] = _create_zones(
        clean_df["pickup_longitude"].values,
        clean_df["pickup_latitude"].values,
        n_zones=n_zones
    )

    logger.info(f"Preprocessed {len(clean_df):,} records ({len(clean_df)/len(df)*100:.1f}% retained)")
    return clean_df


def _create_zones(lon: np.ndarray, lat: np.ndarray, n_zones: int = 5) -> np.ndarray:
    """Create zone IDs based on longitude/latitude grid."""
    lon_bins = np.linspace(-74.05, -73.75, n_zones + 1)
    lat_bins = np.linspace(40.6, 40.9, n_zones + 1)

    lon_zone = np.digitize(lon, lon_bins) - 1
    lat_zone = np.digitize(lat, lat_bins) - 1

    lon_zone = np.clip(lon_zone, 0, n_zones - 1)
    lat_zone = np.clip(lat_zone, 0, n_zones - 1)

    return lat_zone * n_zones + lon_zone


def aggregate_demand(
    df: pd.DataFrame,
    time_col: str = "pickup_datetime",
    zone_col: str = "zone_id",
    freq: str = "h"
) -> pd.DataFrame:
    """
    Aggregate demand by time and zone.

    Args:
        df: Preprocessed DataFrame
        time_col: Timestamp column name
        zone_col: Zone column name
        freq: Aggregation frequency ('h' for hourly)

    Returns:
        Aggregated demand DataFrame
    """
    df = df.copy()
    df["date_hour"] = df[time_col].dt.floor(freq)

    demand_df = df.groupby(["date_hour", zone_col]).agg(
        demand=(time_col, "count"),
        avg_fare=("fare_amount", "mean") if "fare_amount" in df.columns else (time_col, "count")
    ).reset_index()

    # Add time features
    demand_df["hour"] = demand_df["date_hour"].dt.hour
    demand_df["day_of_week"] = demand_df["date_hour"].dt.dayofweek
    demand_df["month"] = demand_df["date_hour"].dt.month
    demand_df["is_weekend"] = demand_df["day_of_week"].isin([5, 6]).astype(int)

    logger.info(f"Aggregated to {len(demand_df):,} time-zone records")
    return demand_df


def create_demand_features(
    df: pd.DataFrame,
    target_col: str = "demand"
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Create features for demand forecasting.

    Args:
        df: Aggregated demand DataFrame
        target_col: Target column name

    Returns:
        Tuple of (DataFrame with features, list of feature column names)
    """
    df = df.copy().sort_values(["zone_id", "date_hour"])

    # Lag features
    df["demand_lag_1"] = df.groupby("zone_id")[target_col].shift(1)
    df["demand_lag_24"] = df.groupby("zone_id")[target_col].shift(24)

    # Rolling features
    df["demand_rolling_mean_24"] = df.groupby("zone_id")[target_col].transform(
        lambda x: x.rolling(24, min_periods=1).mean()
    )

    # Drop NaN
    df = df.dropna()

    feature_cols = [
        "hour", "day_of_week", "month", "is_weekend", "zone_id",
        "demand_lag_1", "demand_lag_24", "demand_rolling_mean_24"
    ]

    logger.info(f"Created {len(feature_cols)} features for {len(df):,} samples")
    return df, feature_cols


def add_rul_to_turbofan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Remaining Useful Life (RUL) column to turbofan data.

    Args:
        df: Turbofan sensor DataFrame

    Returns:
        DataFrame with RUL column
    """
    df = df.copy()

    # Get max cycle for each engine
    max_cycles = df.groupby("unit_id")["time_cycles"].max().reset_index()
    max_cycles.columns = ["unit_id", "max_cycle"]

    # Merge and calculate RUL
    df = df.merge(max_cycles, on="unit_id")
    df["RUL"] = df["max_cycle"] - df["time_cycles"]
    df = df.drop("max_cycle", axis=1)

    logger.info(f"Added RUL: range {df['RUL'].min()} - {df['RUL'].max()}")
    return df


def prepare_rul_features(
    df: pd.DataFrame,
    rul_cap: int = 125
) -> Tuple[pd.DataFrame, List[str], str]:
    """
    Prepare features for RUL prediction.

    Args:
        df: Turbofan DataFrame with RUL
        rul_cap: Maximum RUL value (piece-wise linear)

    Returns:
        Tuple of (DataFrame, feature columns, target column)
    """
    df = df.copy()

    # Clip RUL
    df["RUL_clipped"] = df["RUL"].clip(upper=rul_cap)

    # Select relevant sensors based on typical correlation with RUL
    feature_cols = [
        "time_cycles",
        "op_setting_1", "op_setting_2", "op_setting_3",
        "sensor_2", "sensor_3", "sensor_4", "sensor_7",
        "sensor_11", "sensor_12", "sensor_15", "sensor_17",
        "sensor_20", "sensor_21"
    ]

    # Filter to existing columns
    feature_cols = [c for c in feature_cols if c in df.columns]

    logger.info(f"Prepared {len(feature_cols)} RUL features")
    return df, feature_cols, "RUL_clipped"
