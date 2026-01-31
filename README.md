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
git clone https://github.com/Ashraf0001/Data-Driven-Fleet-Cascade.git
cd Data-Driven-Fleet-Cascade

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

## 📚 Documentation

Full documentation available at: **[https://Ashraf0001.github.io/Data-Driven-Fleet-Cascade](https://Ashraf0001.github.io/Data-Driven-Fleet-Cascade)**

### Documentation Sections

| Section | Description | Link |
|---------|-------------|------|
| **Getting Started** | Installation, quick start, configuration | [View](docs/getting-started/index.md) |
| **Architecture** | System design, data flow, modules | [View](docs/architecture/index.md) |
| **User Guide** | Forecasting, optimization, risk, results | [View](docs/user-guide/index.md) |
| **API Reference** | Endpoints, models, examples | [View](docs/api/index.md) |
| **Developer Guide** | Structure, contributing, testing, code style | [View](docs/developer/index.md) |
| **Operations** | Deployment, monitoring, troubleshooting | [View](docs/operations/index.md) |
| **Reference** | Configuration, data formats, constraints | [View](docs/reference/index.md) |

### Quick Links

**Getting Started:**
- [Installation Guide](docs/getting-started/installation.md)
- [Quick Start](docs/getting-started/quickstart.md)
- [Configuration Guide](docs/getting-started/configuration.md)

**Architecture:**
- [System Overview](docs/architecture/system-overview.md)
- [Data Flow](docs/architecture/data-flow.md)
- [Module Design](docs/architecture/modules.md)

**User Guide:**
- [Demand Forecasting](docs/user-guide/forecasting.md)
- [Fleet Optimization](docs/user-guide/optimization.md)
- [Risk Assessment](docs/user-guide/risk.md)
- [Understanding Results](docs/user-guide/results.md)

**API Reference:**
- [API Endpoints](docs/api/endpoints.md)
- [Request/Response Models](docs/api/models.md)
- [API Examples](docs/api/examples.md)

**Developer Guide:**
- [Project Structure](docs/developer/structure.md)
- [Contributing Guide](docs/developer/contributing.md)
- [Testing Guide](docs/developer/testing.md)
- [Code Style](docs/developer/code-style.md)

**Operations:**
- [Deployment Guide](docs/operations/deployment.md)
- [Monitoring](docs/operations/monitoring.md)
- [Troubleshooting](docs/operations/troubleshooting.md)

**Reference:**
- [Configuration Options](docs/reference/configuration.md)
- [Data Formats](docs/reference/data-formats.md)
- [Constraints Reference](docs/reference/constraints.md)
- [Changelog](docs/reference/changelog.md)

### Serve Documentation Locally

```bash
# Install docs dependencies
uv sync --extra docs

# Serve documentation locally
uv run mkdocs serve

# Build static site
uv run mkdocs build
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
