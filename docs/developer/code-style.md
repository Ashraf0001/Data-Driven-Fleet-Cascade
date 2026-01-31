# Code Style Guide

Coding standards and conventions for the Fleet Decision Platform.

## Overview

We use:
- **PEP 8** for Python style
- **Ruff** for linting and formatting
- **Type hints** everywhere
- **Google-style** docstrings

## Quick Reference

```bash
# Check code style
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/
```

## Python Style

### Imports

```python
# Good: Organized imports
import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter

from src.utils.config import load_config
from src.forecasting.models.base import BaseForecastModel

# Bad: Unorganized
from src.utils.config import load_config
import numpy as np
import logging
from fastapi import APIRouter
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `user_name`, `total_count` |
| Functions | snake_case | `calculate_risk()`, `load_data()` |
| Classes | PascalCase | `DataLoader`, `XGBoostModel` |
| Constants | UPPER_SNAKE | `MAX_RETRIES`, `DEFAULT_PORT` |
| Private | leading underscore | `_internal_method()` |

### Line Length

Maximum 100 characters.

```python
# Good: Line breaks
result = optimizer.optimize(
    demand_forecast=forecasts,
    fleet_state=fleet_state,
    network_costs=network_costs,
    constraints=constraints,
)

# Bad: Too long
result = optimizer.optimize(demand_forecast=forecasts, fleet_state=fleet_state, network_costs=network_costs, constraints=constraints)
```

## Type Hints

### Function Signatures

```python
# Good: Full type hints
def calculate_risk(
    age_days: int,
    utilization: float,
    weights: Dict[str, float],
) -> float:
    """Calculate risk score."""
    ...

# Bad: Missing type hints
def calculate_risk(age_days, utilization, weights):
    ...
```

### Common Types

```python
from typing import Any, Dict, List, Optional, Tuple, Union

# Basic types
name: str
count: int
rate: float
is_active: bool

# Collections
items: List[str]
mapping: Dict[str, int]
coordinates: Tuple[float, float]

# Optional values
config: Optional[Dict[str, Any]] = None

# Union types
id_or_name: Union[int, str]

# Type aliases
Forecast = Dict[str, np.ndarray]
```

### DataFrame Type Hints

```python
import pandas as pd

def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Process input data."""
    ...
```

## Docstrings

### Function Docstrings (Google Style)

```python
def optimize_allocation(
    demand_forecast: Dict[str, np.ndarray],
    fleet_state: pd.DataFrame,
    constraints: Dict[str, float],
) -> pd.DataFrame:
    """Optimize fleet allocation using min-cost flow.

    Finds the optimal vehicle distribution across locations
    to minimize total rebalancing cost while satisfying
    demand and operational constraints.

    Args:
        demand_forecast: Predicted demand by location.
            Keys are location IDs, values are hourly forecasts.
        fleet_state: Current vehicle positions and status.
            Must have columns: vehicle_id, location_id, status.
        constraints: Operational constraints including:
            - max_distance: Maximum rebalancing distance
            - min_service_level: Minimum demand coverage (0-1)

    Returns:
        DataFrame with allocation plan containing:
            - vehicle_id: Vehicle identifier
            - source_location: Current location
            - target_location: Assigned location
            - cost: Movement cost

    Raises:
        ValueError: If demand_forecast is empty.
        OptimizationError: If problem is infeasible.

    Example:
        >>> forecasts = {"1": np.array([10, 15, 20])}
        >>> fleet = pd.DataFrame({"vehicle_id": ["V1"], "location_id": [1]})
        >>> result = optimize_allocation(forecasts, fleet, {"max_distance": 100})
    """
```

### Class Docstrings

```python
class CascadingOptimizer:
    """Multi-stage fleet optimization engine.

    Implements cascading optimization with configurable stages:
    1. Critical demand satisfaction
    2. Min-cost flow rebalancing
    3. MILP refinement (optional)

    Attributes:
        config: Configuration dictionary.
        solver: Underlying optimization solver.
        stages: List of optimization stages to run.

    Example:
        >>> config = load_config()
        >>> optimizer = CascadingOptimizer(config)
        >>> result = optimizer.optimize(forecasts, fleet_state, costs)
    """
```

## Error Handling

### Custom Exceptions

```python
# src/forecasting/exceptions.py
class ForecastError(Exception):
    """Base exception for forecasting module."""
    pass

class ModelNotFittedError(ForecastError):
    """Raised when predicting with unfitted model."""
    pass
```

### Error Handling Pattern

```python
import logging
from src.forecasting.exceptions import ModelNotFittedError

logger = logging.getLogger(__name__)

def predict(self, features: pd.DataFrame) -> np.ndarray:
    """Generate predictions."""
    if not self.is_fitted:
        raise ModelNotFittedError("Model must be fitted before prediction")

    try:
        return self.model.predict(features)
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise ForecastError(f"Prediction failed: {e}") from e
```

## Logging

### Logger Setup

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Process input data."""
    logger.info(f"Processing {len(data)} records")

    try:
        result = transform(data)
        logger.debug(f"Transformation complete: {result.shape}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed diagnostic info |
| INFO | General operational info |
| WARNING | Something unexpected |
| ERROR | Error that was handled |
| CRITICAL | System is unusable |

## Configuration

### Never Hardcode

```python
# Good: Config-driven
config = load_config()
model = XGBoostModel(config["forecasting"]["xgboost"])

# Bad: Hardcoded
model = XGBoostModel({"n_estimators": 100, "max_depth": 6})
```

### Use pathlib

```python
# Good: pathlib.Path
from pathlib import Path

data_dir = Path("data/processed")
model_path = data_dir / "models" / "forecast.pkl"

# Bad: os.path
import os
model_path = os.path.join("data", "processed", "models", "forecast.pkl")
```

## Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "W",      # pycodestyle warnings
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## Pre-commit Hooks

Automatically enforced on commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Next Steps

- [Testing](testing.md) - Testing guide
- [Contributing](contributing.md) - How to contribute
- [Project Structure](structure.md) - Codebase organization
