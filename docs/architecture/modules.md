# Module Design

Detailed design patterns and interfaces for each module.

## Module Structure

```
src/
├── data/           # Data processing
├── forecasting/    # Demand forecasting
├── optimization/   # Optimization engine
├── risk/           # Risk prediction
├── contracts/      # Contract intelligence
├── explainability/ # Explainability
├── api/            # FastAPI application
└── utils/          # Shared utilities
```

## Design Patterns

### Base Model Pattern

All ML models implement a common interface:

```python title="src/forecasting/models/base.py"
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd


class BaseForecastModel(ABC):
    """Abstract base class for forecasting models."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "BaseForecastModel":
        """Train the model."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        pass

    @abstractmethod
    def save(self, path: Path) -> None:
        """Save model to disk."""
        pass

    @abstractmethod
    def load(self, path: Path) -> "BaseForecastModel":
        """Load model from disk."""
        pass

    def get_params(self) -> Dict[str, Any]:
        """Get model parameters."""
        return self.config
```

### Solver Wrapper Pattern

Optimization solvers are wrapped for swappability:

```python title="src/optimization/solvers/base.py"
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import numpy as np


class BaseSolver(ABC):
    """Abstract base class for optimization solvers."""

    @abstractmethod
    def create_model(self) -> Any:
        """Create solver model instance."""
        pass

    @abstractmethod
    def add_variables(
        self,
        num_vars: int,
        lower_bounds: np.ndarray,
        upper_bounds: np.ndarray
    ) -> List[Any]:
        """Add decision variables."""
        pass

    @abstractmethod
    def add_constraint(
        self,
        coefficients: np.ndarray,
        variables: List[Any],
        sense: str,
        rhs: float
    ) -> None:
        """Add a constraint."""
        pass

    @abstractmethod
    def set_objective(
        self,
        coefficients: np.ndarray,
        variables: List[Any],
        sense: str = "minimize"
    ) -> None:
        """Set objective function."""
        pass

    @abstractmethod
    def solve(self) -> Tuple[str, float, np.ndarray]:
        """Solve and return (status, objective_value, solution)."""
        pass
```

### Pipeline Pattern

Data processing follows a pipeline pattern:

```python title="src/data/pipeline.py"
from typing import Callable, List

import pandas as pd


class DataPipeline:
    """Composable data transformation pipeline."""

    def __init__(self):
        self.steps: List[Callable[[pd.DataFrame], pd.DataFrame]] = []

    def add_step(self, func: Callable[[pd.DataFrame], pd.DataFrame]) -> "DataPipeline":
        """Add a transformation step."""
        self.steps.append(func)
        return self

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """Execute all steps in order."""
        result = data
        for step in self.steps:
            result = step(result)
        return result


# Usage example
pipeline = DataPipeline()
pipeline.add_step(clean_missing_values)
pipeline.add_step(add_time_features)
pipeline.add_step(create_lag_features)

processed_data = pipeline.run(raw_data)
```

## Module Interfaces

### Data Module Interface

```python
# src/data/__init__.py
class DataIngestion:
    def load_nyc_taxi(self) -> pd.DataFrame: ...
    def load_nasa_turbofan(self) -> pd.DataFrame: ...

class DataPreprocessor:
    def clean(self, data: pd.DataFrame) -> pd.DataFrame: ...
    def validate(self, data: pd.DataFrame) -> bool: ...

class FleetSimulator:
    def generate_fleet(self, num_vehicles: int) -> pd.DataFrame: ...
    def generate_network_costs(self, num_locations: int) -> np.ndarray: ...
```

### Forecasting Module Interface

```python
# src/forecasting/__init__.py
class ModelTrainer:
    def train(self, data: pd.DataFrame) -> Tuple[BaseForecastModel, Dict]: ...
    def evaluate(self, model: BaseForecastModel, test_data: pd.DataFrame) -> Dict: ...
    def save(self, model: BaseForecastModel, path: Path) -> None: ...

class DemandPredictor:
    def load_model(self, path: Path) -> None: ...
    def predict(self, features: pd.DataFrame, horizon_days: int) -> Dict[str, np.ndarray]: ...
```

### Optimization Module Interface

```python
# src/optimization/__init__.py
class CascadingOptimizer:
    def optimize(
        self,
        demand_forecast: Dict[str, np.ndarray],
        fleet_state: pd.DataFrame,
        network_costs: np.ndarray,
        constraints: Dict[str, float]
    ) -> OptimizationResult: ...

class MinCostFlowSolver:
    def solve(
        self,
        supply: np.ndarray,
        demand: np.ndarray,
        costs: np.ndarray
    ) -> Tuple[np.ndarray, float]: ...
```

### Risk Module Interface

```python
# src/risk/__init__.py
class RiskScorer:
    def calculate(self, fleet_state: pd.DataFrame) -> pd.DataFrame: ...
    def categorize(self, scores: np.ndarray) -> np.ndarray: ...
```

## Error Handling

Each module defines custom exceptions:

```python title="src/forecasting/exceptions.py"
class ForecastError(Exception):
    """Base exception for forecasting module."""
    pass

class ModelNotFittedError(ForecastError):
    """Raised when predicting with unfitted model."""
    pass

class InvalidFeaturesError(ForecastError):
    """Raised when features are invalid."""
    pass
```

```python title="src/optimization/exceptions.py"
class OptimizationError(Exception):
    """Base exception for optimization module."""
    pass

class InfeasibleProblemError(OptimizationError):
    """Raised when optimization problem is infeasible."""
    pass

class SolverTimeoutError(OptimizationError):
    """Raised when solver exceeds time limit."""
    pass
```

## Dependency Injection

Configuration and dependencies are injected:

```python
# Good: Dependency injection
class DemandPredictor:
    def __init__(self, config: Dict[str, Any], model: BaseForecastModel = None):
        self.config = config
        self.model = model

# Bad: Hardcoded dependencies
class DemandPredictor:
    def __init__(self):
        self.config = {"model": "xgboost"}  # Hardcoded!
        self.model = XGBoostModel()  # Tight coupling!
```

## Testing Patterns

Each module should have:

1. **Unit tests** for individual functions
2. **Integration tests** for module interactions
3. **Fixtures** for test data

```python title="tests/unit/test_forecasting.py"
import pytest
from src.forecasting.models.xgboost_model import XGBoostForecastModel


@pytest.fixture
def sample_config():
    return {"n_estimators": 10, "max_depth": 3}


@pytest.fixture
def sample_data():
    # Create small test dataset
    ...


def test_model_fit(sample_config, sample_data):
    model = XGBoostForecastModel(sample_config)
    X, y = sample_data
    model.fit(X, y)
    assert model.is_fitted


def test_model_predict(sample_config, sample_data):
    model = XGBoostForecastModel(sample_config)
    X, y = sample_data
    model.fit(X, y)
    predictions = model.predict(X)
    assert len(predictions) == len(y)
```

## Next Steps

- [System Overview](system-overview.md) - Component details
- [Data Flow](data-flow.md) - Data pipeline
- [API Reference](../api/index.md) - API documentation
