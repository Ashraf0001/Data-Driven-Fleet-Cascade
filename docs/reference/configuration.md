# Configuration Reference

Complete reference for all configuration options.

## Configuration File

Main configuration in `config/config.yaml`:

```yaml
# Full example with all options
data:
  nyc_taxi:
    path: "data/raw/nyc_taxi"
    zones: [1, 2, 3, 4, 5]
    time_range: "2023-01-01:2023-12-31"
    dataset_id: "new-york-city-taxi-fare-prediction"
  nasa_turbofan:
    path: "data/raw/nasa_turbofan"
    dataset_id: "nasa-turbofan-engine-degradation-simulation-data-set"
  processed_path: "data/processed"
  models_path: "data/models"
  outputs_path: "data/outputs"

fleet:
  num_vehicles: 50
  num_locations: 5
  simulation_seed: 42
  vehicle_capacity: 1
  max_travel_distance: 100

forecasting:
  model: "xgboost"
  horizon_days: 7
  features:
    - hour
    - day_of_week
    - month
  xgboost:
    n_estimators: 100
    max_depth: 5
    learning_rate: 0.1

optimization:
  solver: "ortools"
  stages:
    - min_cost_flow
  constraints_file: "config/constraints/fleet_constraints.json"

risk:
  model: "heuristic"
  heuristic_threshold: 0.8

api:
  host: "0.0.0.0"
  port: 8000
  log_level: "INFO"

logging:
  version: 1
  disable_existing_loggers: false
```

---

## Data Configuration

### NYC Taxi Data

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path` | string | `"data/raw/nyc_taxi"` | Storage path |
| `zones` | list[int] | `[1,2,3,4,5]` | Taxi zone IDs |
| `time_range` | string | `"2023-01-01:2023-12-31"` | Date range |
| `dataset_id` | string | - | Kaggle dataset ID |

### NASA Turbofan Data

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path` | string | `"data/raw/nasa_turbofan"` | Storage path |
| `dataset_id` | string | - | Kaggle dataset ID |

### Paths

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `processed_path` | string | `"data/processed"` | Processed data |
| `models_path` | string | `"data/models"` | Model artifacts |
| `outputs_path` | string | `"data/outputs"` | Generated outputs |

---

## Fleet Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `num_vehicles` | int | `50` | Total vehicles in fleet |
| `num_locations` | int | `5` | Number of service locations |
| `simulation_seed` | int | `42` | Random seed for reproducibility |
| `vehicle_capacity` | int | `1` | Passengers per vehicle |
| `max_travel_distance` | float | `100` | Max rebalancing distance (km) |

---

## Forecasting Configuration

### General

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"xgboost"` | Model type: `xgboost`, `prophet`, `tft` |
| `horizon_days` | int | `7` | Forecast horizon |
| `features` | list[str] | `[hour, day_of_week, month]` | Feature columns |

### XGBoost Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `n_estimators` | int | `100` | Number of trees |
| `max_depth` | int | `5` | Maximum tree depth |
| `learning_rate` | float | `0.1` | Learning rate |
| `min_child_weight` | int | `1` | Min child weight |
| `subsample` | float | `0.8` | Row subsampling |
| `colsample_bytree` | float | `0.8` | Column subsampling |

### Prophet Options (Phase 2)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `seasonality_mode` | string | `"multiplicative"` | Seasonality type |
| `changepoint_prior_scale` | float | `0.05` | Trend flexibility |
| `yearly_seasonality` | bool | `true` | Include yearly seasonality |
| `weekly_seasonality` | bool | `true` | Include weekly seasonality |
| `daily_seasonality` | bool | `true` | Include daily seasonality |

---

## Optimization Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `solver` | string | `"ortools"` | Solver: `ortools`, `pulp` |
| `stages` | list[str] | `["min_cost_flow"]` | Optimization stages |
| `constraints_file` | string | `"config/constraints/..."` | Constraints JSON file |

### Solver Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `time_limit_seconds` | int | `60` | Max solve time |
| `optimality_gap` | float | `0.01` | Gap tolerance (1%) |
| `num_threads` | int | `4` | Parallel threads |

### Optimization Stages

| Stage | Description | Phase |
|-------|-------------|-------|
| `min_cost_flow` | Minimize rebalancing cost | MVP |
| `critical_demand` | Ensure service levels | Phase 2 |
| `milp_refinement` | Handle discrete constraints | Phase 4 |

---

## Risk Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"heuristic"` | Model type |
| `heuristic_threshold` | float | `0.8` | High risk threshold |

### Heuristic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `age_weight` | float | `0.3` | Weight for vehicle age |
| `utilization_weight` | float | `0.4` | Weight for utilization |
| `maintenance_weight` | float | `0.3` | Weight for maintenance history |

### Thresholds

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `high` | float | `0.7` | High risk threshold |
| `medium` | float | `0.4` | Medium risk threshold |
| `low` | float | `0.0` | Low risk threshold |

---

## API Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `"0.0.0.0"` | Bind host |
| `port` | int | `8000` | Bind port |
| `log_level` | string | `"INFO"` | Log level |
| `debug` | bool | `false` | Enable debug mode |
| `reload` | bool | `false` | Auto-reload on changes |

### CORS Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allow_origins` | list[str] | `["*"]` | Allowed origins |
| `allow_methods` | list[str] | `["*"]` | Allowed methods |
| `allow_headers` | list[str] | `["*"]` | Allowed headers |

---

## Logging Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `version` | int | `1` | Config version |
| `disable_existing_loggers` | bool | `false` | Disable other loggers |

### Log Levels

| Level | Value |
|-------|-------|
| DEBUG | 10 |
| INFO | 20 |
| WARNING | 30 |
| ERROR | 40 |
| CRITICAL | 50 |

---

## Environment Variables

Override configuration with environment variables:

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fleet_db
POSTGRES_USER=fleet_user
POSTGRES_PASSWORD=secret

# Cache
REDIS_HOST=localhost
REDIS_PORT=6379

# API
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Data
KAGGLE_USERNAME=username
KAGGLE_KEY=api_key
```

## Next Steps

- [Data Formats](data-formats.md) - Data schemas
- [Constraints](constraints.md) - Constraint reference
