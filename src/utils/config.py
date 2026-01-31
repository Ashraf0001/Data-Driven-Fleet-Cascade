"""Configuration loading utilities."""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def load_config(config_path: str | Path = "config/config.yaml") -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    # Load environment variables
    load_dotenv()

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Substitute environment variables
    config = _substitute_env_vars(config)

    return config


def _substitute_env_vars(config: Any) -> Any:
    """Recursively substitute environment variables in config.

    Environment variables are specified as ${VAR_NAME} in the config.

    Args:
        config: Configuration value (dict, list, or scalar)

    Returns:
        Configuration with environment variables substituted
    """
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_name = config[2:-1]
        return os.getenv(var_name, config)
    return config


def get_config_value(config: dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get a nested configuration value using dot notation.

    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the value (e.g., "forecasting.model")
        default: Default value if key doesn't exist

    Returns:
        Configuration value or default

    Example:
        >>> config = {"forecasting": {"model": "xgboost"}}
        >>> get_config_value(config, "forecasting.model")
        'xgboost'
    """
    keys = key_path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value
