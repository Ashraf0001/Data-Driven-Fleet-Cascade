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

from src.data.loader import (
    generate_fleet_state,
    generate_location_metadata,
    generate_network_costs,
)
from src.utils.config import get_config, get_config_value


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    config = get_config()
    default_num_vehicles = get_config_value(config, "data.fleet.num_vehicles", 50)
    default_num_locations = get_config_value(config, "data.fleet.locations", 5)
    default_seed = get_config_value(config, "data.fleet.simulation_seed", 42)

    parser = argparse.ArgumentParser(description="Generate simulated fleet data")
    parser.add_argument(
        "--num-vehicles",
        type=int,
        default=default_num_vehicles,
        help="Number of vehicles (default: config value)",
    )
    parser.add_argument(
        "--num-locations",
        type=int,
        default=default_num_locations,
        help="Number of locations (default: config value)",
    )
    parser.add_argument(
        "--seed", type=int, default=default_seed, help="Random seed (default: config value)"
    )
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
        n_vehicles=args.num_vehicles,
        n_zones=args.num_locations,
        seed=args.seed,
        status_distribution=get_config_value(config, "data.fleet.status_distribution", None),
    )
    fleet_df["location_id"] = fleet_df["current_zone"] + 1
    fleet_df["age_days"] = fleet_df["age_months"] * 30
    fleet_df["utilization_rate"] = np.clip(
        np.random.normal(0.7, 0.15, len(fleet_df)), 0.1, 1.0
    ).round(3)
    fleet_df["last_maintenance_days"] = np.random.randint(0, 30, len(fleet_df))
    fleet_path = output_dir / "fleet_state.parquet"
    fleet_df.to_parquet(fleet_path, index=False)
    logger.info(f"Fleet state saved to: {fleet_path}")

    # Generate network costs
    costs = generate_network_costs(
        n_zones=args.num_locations,
        seed=args.seed,
    )
    costs_path = output_dir / "network_costs.npy"
    np.save(costs_path, costs)
    logger.info(f"Network costs saved to: {costs_path}")

    # Generate location metadata
    locations_df = generate_location_metadata(
        n_locations=args.num_locations,
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
