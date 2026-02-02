# Fleet Decision Platform

> A simple, end-to-end decision system for fleet operations: forecast demand, optimize allocations,
> and score fleet risk — all from a single, config-driven pipeline.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Why this exists

Fleet teams often have demand forecasts, vehicle constraints, and maintenance needs scattered
across tools. This project brings them together so you can:

- **Predict demand** by zone and time
- **Allocate vehicles** with a cost-aware optimizer
- **Score risk** to prioritize maintenance
- **Explain outcomes** with KPIs and allocation details

## What you can run today

MVP focuses on a clean, working pipeline:

- **Forecasting:** heuristic + XGBoost ready
- **Optimization:** min-cost flow allocation
- **Risk:** heuristic scoring
- **API:** FastAPI endpoints
- **UI:** Streamlit dashboard

## Quick start (local)

```bash
git clone https://github.com/Ashraf0001/Data-Driven-Fleet-Cascade.git
cd Data-Driven-Fleet-Cascade

# Core deps
uv sync

# API + ML + UI + dev tools
uv sync --extra api --extra ml --extra dashboard --extra dev
```

### Start the API

```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

### Start the dashboard

```bash
# If your API runs on a different port:
# API_BASE_URL="http://127.0.0.1:8001"
API_BASE_URL="http://127.0.0.1:8000" uv run streamlit run app.py
```

### Try the API

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/config
```

## Guided walkthrough

Open the notebook for a single, end-to-end explanation:
`fleet_cascade_overview.ipynb`

## Configuration

All behavior is driven by `config/config.yaml`.

Example:

```yaml
forecasting:
  model: "xgboost"
  horizon_days: 7

optimization:
  solver: "ortools"
  constraints:
    max_cost_per_vehicle: 50.0
    min_service_level: 0.0

risk:
  model: "heuristic"
  thresholds:
    high: 0.7
    medium: 0.4
    low: 0.0
```

## Project structure (simplified)

```
Data-Driven-Fleet-Cascade/
├── app.py                  # Streamlit dashboard
├── config/                 # Config files
├── docs/                   # MkDocs site
├── scripts/                # CLI helpers
├── src/                    # Core logic + API
└── tests/                  # Tests
```

## Tests

```bash
uv run pytest
```

## Docs

```bash
uv sync --extra docs
uv run mkdocs serve
```

## Links

- Docs: https://Ashraf0001.github.io/Data-Driven-Fleet-Cascade
- API docs (local): http://localhost:8000/docs
- GitHub: https://github.com/Ashraf0001/Data-Driven-Fleet-Cascade

## License

MIT License — see `LICENSE`.
