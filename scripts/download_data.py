#!/usr/bin/env python
"""Download datasets from Kaggle.

This script downloads the NYC Taxi and NASA Turbofan datasets
required for the Fleet Decision Platform.

Usage:
    uv run python scripts/download_data.py
    uv run python scripts/download_data.py --dataset nyc_taxi
    uv run python scripts/download_data.py --dataset nasa_turbofan
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Dataset configurations
DATASETS = {
    "nyc_taxi": {
        "kaggle_id": "elemento/nyc-yellow-taxi-trip-data",  # Example - update with actual ID
        "output_dir": "data/raw/nyc_taxi",
        "description": "NYC Yellow Taxi Trip Data",
    },
    "nasa_turbofan": {
        "kaggle_id": "behrad3d/nasa-cmaps",  # Example - update with actual ID
        "output_dir": "data/raw/nasa_turbofan",
        "description": "NASA Turbofan Engine Degradation Dataset",
    },
}


def check_kaggle_credentials() -> bool:
    """Check if Kaggle credentials are configured."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if kaggle_json.exists():
        logger.info("Kaggle credentials found at ~/.kaggle/kaggle.json")
        return True

    # Check environment variables
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        logger.info("Kaggle credentials found in environment variables")
        return True

    logger.error(
        "Kaggle credentials not found. Please either:\n"
        "1. Create ~/.kaggle/kaggle.json with your credentials, or\n"
        "2. Set KAGGLE_USERNAME and KAGGLE_KEY environment variables"
    )
    return False


def download_dataset(dataset_name: str) -> bool:
    """Download a dataset from Kaggle.

    Args:
        dataset_name: Name of the dataset to download

    Returns:
        True if download was successful, False otherwise
    """
    if dataset_name not in DATASETS:
        logger.error(f"Unknown dataset: {dataset_name}")
        logger.info(f"Available datasets: {list(DATASETS.keys())}")
        return False

    config = DATASETS[dataset_name]
    output_dir = Path(config["output_dir"])

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading {config['description']}...")
    logger.info(f"Kaggle dataset: {config['kaggle_id']}")
    logger.info(f"Output directory: {output_dir}")

    try:
        # Run Kaggle CLI command
        cmd = [
            "kaggle",
            "datasets",
            "download",
            "-d",
            config["kaggle_id"],
            "-p",
            str(output_dir),
            "--unzip",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Download failed: {result.stderr}")
            return False

        logger.info(f"Successfully downloaded {dataset_name}")
        logger.info(f"Files saved to: {output_dir}")

        # List downloaded files
        files = list(output_dir.glob("*"))
        logger.info(f"Downloaded files: {[f.name for f in files]}")

        return True

    except FileNotFoundError:
        logger.error("Kaggle CLI not found. Install it with: uv add kaggle")
        return False
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Download datasets for Fleet Decision Platform")
    parser.add_argument(
        "--dataset",
        choices=list(DATASETS.keys()) + ["all"],
        default="all",
        help="Dataset to download (default: all)",
    )
    args = parser.parse_args()

    # Check credentials
    if not check_kaggle_credentials():
        sys.exit(1)

    # Determine which datasets to download
    if args.dataset == "all":
        datasets_to_download = list(DATASETS.keys())
    else:
        datasets_to_download = [args.dataset]

    # Download datasets
    success = True
    for dataset in datasets_to_download:
        if not download_dataset(dataset):
            success = False

    if success:
        logger.info("All datasets downloaded successfully!")
    else:
        logger.warning("Some datasets failed to download")
        sys.exit(1)


if __name__ == "__main__":
    main()
