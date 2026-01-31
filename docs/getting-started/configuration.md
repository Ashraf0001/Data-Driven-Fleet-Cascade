# Configuration

The Fleet Decision Platform is highly configurable through YAML files and environment variables.

## Configuration Files

| File | Purpose |
|------|---------|
| `config/config.yaml` | Main configuration |
| `config/constraints/fleet_constraints.json` | Fleet operational constraints |
| `.env` | Environment variables (secrets) |

## Main Configuration

The primary configuration file is `config/config.yaml`:

```yaml title="config/config.yaml"
# Data sources
data:
  nyc_taxi:
    path: "data/raw/nyc_taxi"
    zones: [4, 12, 13, 68, 79]  # NYC taxi zones
    time_range: "2023-01-01:2023-03-31"
    aggregation: "hourly"

  fleet:
    num_vehicles: 50
    locations: 5
    simulation_seed: 42

# Forecasting settings
forecasting:
  model: "xgboost"  # Options: xgboost, prophet, tft
  horizon_days: 7
  features:
    - hour
    - day_of_week
    - month
    - is_weekend

# Optimization settings
optimization:
  solver: "ortools"  # Options: ortools, pulp
  stages:
    - min_cost_flow
  constraints:
    max_distance: 100
    capacity_per_vehicle: 1
    min_service_level: 0.95
```

## Configuration Sections

### Data Configuration

Controls data sources and processing:

```yaml
data:
  nyc_taxi:
    path: "data/raw/nyc_taxi"    # Data location
    zones: [4, 12, 13, 68, 79]   # Taxi zones to use
    time_range: "2023-01-01:2023-03-31"  # Date range
    aggregation: "hourly"         # hourly or daily

  fleet:
    num_vehicles: 50              # Total fleet size
    locations: 5                  # Number of zones
    capacity_per_vehicle: 1       # Passengers per vehicle
    simulation_seed: 42           # For reproducibility
```

### Forecasting Configuration

Controls demand forecasting models:

```yaml
forecasting:
  model: "xgboost"    # Model type
  horizon_days: 7     # Forecast horizon

  features:           # Features for model
    - hour
    - day_of_week
    - month
    - is_weekend
    - lag_1h
    - lag_24h

  xgboost:            # XGBoost hyperparameters
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1
```

### Optimization Configuration

Controls the optimization engine:

```yaml
optimization:
  solver: "ortools"   # Solver library

  stages:             # Optimization stages
    - min_cost_flow   # MVP: single stage
    # - critical_demand  # Phase 2+
    # - milp_refinement  # Phase 4

  constraints:
    max_distance: 100           # Max rebalancing distance
    capacity_per_vehicle: 1     # Vehicle capacity
    min_service_level: 0.95     # 95% demand coverage

  solver_settings:
    time_limit_seconds: 60      # Solver timeout
    optimality_gap: 0.01        # 1% gap tolerance
```

### API Configuration

Controls the FastAPI server:

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  debug: true
  reload: true

  cors:
    allow_origins: ["*"]
    allow_methods: ["*"]
    allow_headers: ["*"]
```

### Logging Configuration

Controls logging behavior:

```yaml
logging:
  level: "INFO"       # DEBUG, INFO, WARNING, ERROR
  format: "text"      # text (dev) or json (prod)

  file:
    enabled: false
    path: "logs/fleet_cascade.log"
```

## Environment Variables

Sensitive configuration uses environment variables in `.env`:

```bash title=".env"
# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fleet_db
POSTGRES_USER=fleet_user
POSTGRES_PASSWORD=secure_password

# API
API_DEBUG=true
LOG_LEVEL=INFO
```

### Using Environment Variables in Config

Reference environment variables with `${VAR_NAME}`:

```yaml
database:
  postgresql:
    host: "${POSTGRES_HOST}"
    password: "${POSTGRES_PASSWORD}"
```

## Constraint Configuration

Fleet constraints in `config/constraints/fleet_constraints.json`:

```json title="config/constraints/fleet_constraints.json"
{
  "capacity_constraints": {
    "max_vehicles_per_location": 20,
    "min_vehicles_per_location": 2,
    "total_fleet_size": 50
  },
  "operational_constraints": {
    "max_rebalancing_distance_km": 100,
    "max_daily_trips_per_vehicle": 10
  },
  "service_level_constraints": {
    "min_demand_coverage": 0.95,
    "max_wait_time_minutes": 15
  },
  "cost_constraints": {
    "max_rebalancing_cost_per_day": 10000,
    "cost_per_km": 0.5
  }
}
```

## Configuration Profiles

Use different configurations for different environments:

=== "Development"

    ```yaml title="config/config.yaml"
    api:
      debug: true
      reload: true
    logging:
      level: "DEBUG"
      format: "text"
    ```

=== "Production"

    ```yaml title="config/config.prod.yaml"
    api:
      debug: false
      reload: false
    logging:
      level: "INFO"
      format: "json"
    ```

Load different configs:

```python
from src.utils.config import load_config

# Development (default)
config = load_config("config/config.yaml")

# Production
config = load_config("config/config.prod.yaml")
```

## Validating Configuration

Check your configuration is valid:

```bash
uv run python -c "
from src.utils.config import load_config
config = load_config()
print('✓ Configuration is valid')
print(f'  Zones: {config[\"data\"][\"nyc_taxi\"][\"zones\"]}')
print(f'  Model: {config[\"forecasting\"][\"model\"]}')
print(f'  Solver: {config[\"optimization\"][\"solver\"]}')
"
```

## Best Practices

!!! tip "Configuration Best Practices"

    1. **Never hardcode** - Always use config files
    2. **Use environment variables** for secrets
    3. **Version control** config files (except `.env`)
    4. **Document** custom configuration options
    5. **Validate** configuration at startup

## Next Steps

- [Quick Start](quickstart.md) - Run the platform
- [Architecture](../architecture/index.md) - Understand the system
- [API Reference](../api/index.md) - Explore endpoints
