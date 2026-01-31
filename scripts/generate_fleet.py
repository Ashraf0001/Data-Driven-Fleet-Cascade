#!/usr/bin/env python
"""Generate simulated fleet data.

This script generates synthetic fleet state data including:
- Vehicle inventory per location
- Network cost matrices
- Initial fleet distribution

Usage:
    uv run python scripts/generate_fleet.py
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_fleet_state(
    num_vehicles: int = 50,
    num_locations: int = 5,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate fleet state DataFrame.

    Args:
        num_vehicles: Total number of vehicles
        num_locations: Number of locations/zones
        seed: Random seed for reproducibility

    Returns:
        DataFrame with vehicle information
    """
    np.random.seed(seed)

    # Distribute vehicles across locations
    location_ids = np.random.choice(
        range(1, num_locations + 1),
        size=num_vehicles,
        p=np.ones(num_locations) / num_locations,  # Uniform distribution
    )

    # Generate vehicle statuses
    status_choices = ["operational", "maintenance", "downtime"]
    status_probs = [0.85, 0.10, 0.05]
    statuses = np.random.choice(status_choices, size=num_vehicles, p=status_probs)

    # Generate vehicle ages (in days)
    ages = np.random.exponential(scale=365, size=num_vehicles).astype(int)

    # Generate utilization rates
    utilization = np.clip(np.random.normal(0.7, 0.15, num_vehicles), 0.1, 1.0)

    fleet_df = pd.DataFrame(
        {
            "vehicle_id": [f"V{i:04d}" for i in range(num_vehicles)],
            "location_id": location_ids,
            "capacity": 1,
            "status": statuses,
            "age_days": ages,
            "utilization_rate": utilization.round(3),
            "last_maintenance_days": np.random.randint(0, 30, num_vehicles),
        }
    )

    return fleet_df


def generate_network_costs(
    num_locations: int = 5,
    seed: int = 42,
) -> np.ndarray:
    """Generate zone-to-zone cost matrix.

    Args:
        num_locations: Number of locations/zones
        seed: Random seed for reproducibility

    Returns:
        2D numpy array of costs
    """
    np.random.seed(seed)

    # Generate random coordinates for locations
    coords = np.random.rand(num_locations, 2) * 100  # 100km x 100km area

    # Calculate Euclidean distances
    costs = np.zeros((num_locations, num_locations))
    for i in range(num_locations):
        for j in range(num_locations):
            if i != j:
                dist = np.sqrt(np.sum((coords[i] - coords[j]) ** 2))
                # Add some randomness to costs (traffic, etc.)
                costs[i, j] = dist * np.random.uniform(0.9, 1.1)

    return costs.round(2)


def generate_location_metadata(
    num_locations: int = 5,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate location metadata.

    Args:
        num_locations: Number of locations/zones
        seed: Random seed for reproducibility

    Returns:
        DataFrame with location information
    """
    np.random.seed(seed)

    # NYC-inspired zone names
    zone_names = [
        "Manhattan-Midtown",
        "Manhattan-Downtown",
        "Brooklyn-Heights",
        "Queens-Astoria",
        "Bronx-South",
        "Manhattan-Uptown",
        "Brooklyn-Downtown",
        "Queens-LIC",
        "Staten-Island",
        "JFK-Airport",
    ]

    locations_df = pd.DataFrame(
        {
            "location_id": range(1, num_locations + 1),
            "name": zone_names[:num_locations],
            "latitude": 40.7 + np.random.uniform(-0.1, 0.1, num_locations),
            "longitude": -74.0 + np.random.uniform(-0.1, 0.1, num_locations),
            "avg_demand": np.random.randint(50, 200, num_locations),
            "max_capacity": np.random.randint(15, 30, num_locations),
        }
    )

    return locations_df


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate simulated fleet data")
    parser.add_argument(
        "--num-vehicles", type=int, default=50, help="Number of vehicles (default: 50)"
    )
    parser.add_argument(
        "--num-locations", type=int, default=5, help="Number of locations (default: 5)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed/fleet_state",
        help="Output directory (default: data/processed/fleet_state)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Generating fleet data with {args.num_vehicles} vehicles "
        f"across {args.num_locations} locations..."
    )

    # Generate fleet state
    fleet_df = generate_fleet_state(
        num_vehicles=args.num_vehicles,
        num_locations=args.num_locations,
        seed=args.seed,
    )
    fleet_path = output_dir / "fleet_state.parquet"
    fleet_df.to_parquet(fleet_path, index=False)
    logger.info(f"Fleet state saved to: {fleet_path}")

    # Generate network costs
    costs = generate_network_costs(
        num_locations=args.num_locations,
        seed=args.seed,
    )
    costs_path = output_dir / "network_costs.npy"
    np.save(costs_path, costs)
    logger.info(f"Network costs saved to: {costs_path}")

    # Generate location metadata
    locations_df = generate_location_metadata(
        num_locations=args.num_locations,
        seed=args.seed,
    )
    locations_path = output_dir / "locations.parquet"
    locations_df.to_parquet(locations_path, index=False)
    logger.info(f"Location metadata saved to: {locations_path}")

    # Summary
    logger.info("\n=== Generated Data Summary ===")
    logger.info(f"Fleet size: {len(fleet_df)} vehicles")
    logger.info(f"Locations: {args.num_locations}")
    logger.info(f"Operational vehicles: {(fleet_df['status'] == 'operational').sum()}")
    logger.info(f"Average utilization: {fleet_df['utilization_rate'].mean():.2%}")

    logger.info("\nFleet distribution by location:")
    for loc_id, count in fleet_df.groupby("location_id").size().items():
        logger.info(f"  Location {loc_id}: {count} vehicles")


if __name__ == "__main__":
    main()
