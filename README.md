# Fleet Decision Platform

> Enterprise-grade decision intelligence platform for fleet operations

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Overview

A modular, config-driven platform that transforms demand forecasts, contract rules, and risk predictions into explainable, cost-optimized fleet allocation decisions.

### Core Capabilities

- **Demand Forecasting**: Multi-location time-series forecasting with XGBoost/Prophet
- **Cascading Optimization**: Multi-stage optimization (min-cost flow + MILP)
- **Contract Intelligence**: NLP/Vision extraction from contract PDFs (Phase 3+)
- **Risk Prediction**: Asset failure and contract violation prediction
- **Explainability**: SHAP analysis, constraint analysis, cost drivers

## Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fleet-cascade.git
cd fleet-cascade

# Install dependencies with uv
uv sync

# Install development dependencies
uv sync --all-extras

# Set up pre-commit hooks (optional but recommended)
uv run pre-commit install
```

### Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   - Kaggle API credentials (for data download)
   - Database credentials (if using PostgreSQL)

3. Review `config/config.yaml` for model and optimization parameters.

### Download Data

```bash
# Download NYC Taxi data and NASA Turbofan dataset
uv run python scripts/download_data.py
```

### Run the Pipeline

```bash
# Run the full optimization pipeline
uv run python scripts/run_pipeline.py

# Or start the API server
uv run uvicorn src.api.main:app --reload
```

## Project Structure

```
fleet-cascade/
├── config/                 # Configuration files
│   └── config.yaml        # Main configuration
├── data/                   # Data directory (gitignored)
│   ├── raw/               # Raw data files
│   ├── processed/         # Processed data
│   ├── models/            # Trained models
│   └── outputs/           # Generated outputs
├── src/                    # Source code
│   ├── data/              # Data processing
│   ├── forecasting/       # Demand forecasting
│   ├── optimization/      # Optimization engine
│   ├── risk/              # Risk prediction
│   ├── explainability/    # Explainability modules
│   ├── api/               # FastAPI application
│   └── utils/             # Shared utilities
├── tests/                  # Test suite
├── scripts/                # Utility scripts
└── docs/                   # Documentation
```

## Development

### Common Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Run API server (development)
uv run uvicorn src.api.main:app --reload --port 8000
```

### Using Makefile

```bash
make install      # Install dependencies
make test         # Run tests
make lint         # Lint and format code
make run          # Run API server
make download     # Download datasets
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/optimize` | POST | Run optimization pipeline |
| `/api/v1/forecast` | POST | Generate demand forecasts |
| `/docs` | GET | OpenAPI documentation |

## Configuration

Key configuration options in `config/config.yaml`:

```yaml
data:
  nyc_taxi:
    zones: [1, 2, 3, 4, 5]
    time_range: "2023-01-01:2023-03-31"

forecasting:
  model: "xgboost"
  horizon_days: 7

optimization:
  solver: "ortools"
  constraints:
    max_distance: 100
    capacity_per_vehicle: 1
```

## Phased Development

- **Phase 1 (MVP)**: Basic forecasting + single-stage optimization
- **Phase 2**: Hierarchical forecasting + cascading optimization + SHAP
- **Phase 3**: Contract intelligence (OCR + NLP)
- **Phase 4**: Production deployment + advanced features

## Documentation

Full documentation available at: [Documentation Site](https://yourusername.github.io/fleet-cascade)

```bash
# Serve documentation locally
uv run mkdocs serve
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NYC Taxi & Limousine Commission for trip data
- NASA for turbofan degradation dataset
- Open source community for amazing tools
