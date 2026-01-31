# Testing Guide

Comprehensive guide to testing the Fleet Decision Platform.

## Testing Stack

| Tool | Purpose |
|------|---------|
| pytest | Test framework |
| pytest-cov | Coverage reporting |
| pytest-asyncio | Async test support |
| httpx | API testing |

## Running Tests

### All Tests

```bash
# Run all tests
uv run pytest

# Verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Specific Tests

```bash
# Single file
uv run pytest tests/unit/test_forecasting.py

# Single test
uv run pytest tests/unit/test_forecasting.py::test_model_fit

# By marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── fixtures/             # Test data files
│   └── sample_data.json
├── unit/                 # Unit tests
│   ├── __init__.py
│   ├── test_forecasting.py
│   ├── test_optimization.py
│   └── test_risk.py
└── integration/          # Integration tests
    ├── __init__.py
    └── test_pipeline.py
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_forecasting.py
import pytest
import numpy as np
import pandas as pd

from src.forecasting.models.xgboost_model import XGBoostForecastModel


class TestXGBoostModel:
    """Tests for XGBoost forecasting model."""

    def test_model_initialization(self, sample_config):
        """Test model initializes with config."""
        model = XGBoostForecastModel(sample_config)

        assert model.config == sample_config
        assert model.model is None
        assert model.is_fitted is False

    def test_model_fit(self, sample_config, sample_features):
        """Test model training."""
        model = XGBoostForecastModel(sample_config)
        X, y = sample_features

        model.fit(X, y)

        assert model.is_fitted is True
        assert model.model is not None

    def test_model_predict(self, trained_model, sample_features):
        """Test model prediction."""
        X, y = sample_features

        predictions = trained_model.predict(X)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(y)
        assert all(p >= 0 for p in predictions)

    def test_model_predict_untrained_raises(self, sample_config, sample_features):
        """Test that predicting with untrained model raises error."""
        model = XGBoostForecastModel(sample_config)
        X, _ = sample_features

        with pytest.raises(RuntimeError, match="not fitted"):
            model.predict(X)
```

### Integration Test Example

```python
# tests/integration/test_pipeline.py
import pytest

from src.utils.config import load_config
from src.data.ingestion import DataIngestion
from src.forecasting import DemandPredictor
from src.optimization import CascadingOptimizer


@pytest.mark.integration
class TestPipeline:
    """Integration tests for full pipeline."""

    def test_end_to_end_pipeline(self, temp_data_dir):
        """Test complete pipeline from data to optimization."""
        # Load config
        config = load_config("config/config.yaml")

        # Generate test data
        from scripts.generate_fleet import (
            generate_fleet_state,
            generate_network_costs
        )
        fleet_state = generate_fleet_state(num_vehicles=10)
        network_costs = generate_network_costs(num_locations=3)

        # Create mock forecasts
        forecasts = {
            "1": [10, 12, 15, 18, 15, 12, 10],
            "2": [8, 10, 12, 14, 12, 10, 8],
            "3": [5, 6, 8, 10, 8, 6, 5],
        }

        # Run optimization
        optimizer = CascadingOptimizer(config)
        result = optimizer.optimize(
            demand_forecast=forecasts,
            fleet_state=fleet_state,
            network_costs=network_costs
        )

        # Verify results
        assert result.status == "success"
        assert result.total_cost >= 0
        assert len(result.allocation_plan) > 0
        assert 0 <= result.kpis["demand_coverage"] <= 1
```

### API Test Example

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIEndpoints:
    """Tests for API endpoints."""

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_optimization_endpoint(self, client):
        """Test optimization endpoint."""
        request_data = {
            "demand_forecast": {
                "1": [10, 15, 20],
                "2": [8, 12, 16]
            },
            "fleet_state": {
                "vehicles": [
                    {"id": "V001", "location": 1, "capacity": 1}
                ]
            },
            "constraints": {
                "max_distance": 100
            }
        }

        response = client.post("/api/v1/optimize", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "allocation_plan" in data["data"]
```

## Fixtures

### Shared Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "forecasting": {
            "model": "xgboost",
            "xgboost": {
                "n_estimators": 10,
                "max_depth": 3
            }
        }
    }


@pytest.fixture
def sample_features():
    """Sample feature data for testing."""
    np.random.seed(42)
    n_samples = 100

    X = pd.DataFrame({
        "hour": np.random.randint(0, 24, n_samples),
        "day_of_week": np.random.randint(0, 7, n_samples),
        "lag_1h": np.random.rand(n_samples) * 20
    })
    y = np.random.poisson(10, n_samples).astype(float)

    return X, y


@pytest.fixture
def trained_model(sample_config, sample_features):
    """Pre-trained model for testing."""
    from src.forecasting.models.xgboost_model import XGBoostForecastModel

    model = XGBoostForecastModel(sample_config)
    X, y = sample_features
    model.fit(X, y)

    return model
```

## Test Markers

```python
# pytest.ini (in pyproject.toml)
[tool.pytest.ini_options]
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "slow: marks tests as slow",
]
```

Usage:

```python
@pytest.mark.unit
def test_fast_function():
    pass

@pytest.mark.integration
def test_full_pipeline():
    pass

@pytest.mark.slow
def test_large_optimization():
    pass
```

## Coverage

### Generate Coverage Report

```bash
# Terminal report
uv run pytest --cov=src --cov-report=term

# HTML report
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Coverage Targets

| Module | Target |
|--------|--------|
| `src/utils/` | > 90% |
| `src/data/` | > 80% |
| `src/forecasting/` | > 80% |
| `src/optimization/` | > 75% |
| `src/api/` | > 85% |

## Best Practices

!!! tip "Test Isolation"

    - Each test should be independent
    - Use fixtures for setup/teardown
    - Don't share state between tests

!!! tip "Test Naming"

    - Use descriptive names: `test_model_predict_with_empty_input_raises_error`
    - Follow pattern: `test_<function>_<scenario>_<expected_result>`

!!! tip "Test Data"

    - Use small, focused datasets
    - Generate data in fixtures
    - Avoid external dependencies

## Next Steps

- [Code Style](code-style.md) - Coding standards
- [Contributing](contributing.md) - How to contribute
- [Project Structure](structure.md) - Codebase organization
