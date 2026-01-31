# Data Formats Reference

Complete reference for all data schemas and formats.

## Storage Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| Parquet | `.parquet` | Processed data, features |
| NumPy | `.npy` | Matrices, arrays |
| JSON | `.json` | Configuration, metadata |
| Pickle | `.pkl` | Model artifacts |

---

## Input Data

### NYC Taxi Data

Raw trip data from NYC TLC:

```python
pd.DataFrame({
    "pickup_datetime": pd.Timestamp,   # Trip start time
    "dropoff_datetime": pd.Timestamp,  # Trip end time
    "pickup_location_id": int,         # Pickup zone (1-263)
    "dropoff_location_id": int,        # Dropoff zone (1-263)
    "trip_distance": float,            # Miles
    "passenger_count": int,            # Number of passengers
    "fare_amount": float,              # Trip fare
})
```

**Example:**

| pickup_datetime | dropoff_datetime | pickup_location_id | dropoff_location_id | trip_distance |
|-----------------|------------------|-------------------|---------------------|---------------|
| 2023-01-01 08:15 | 2023-01-01 08:32 | 79 | 234 | 3.2 |

### NASA Turbofan Data

Engine degradation dataset:

```python
pd.DataFrame({
    "unit_number": int,      # Engine unit ID
    "time_cycles": int,      # Operating cycles
    "setting_1": float,      # Operational setting 1
    "setting_2": float,      # Operational setting 2
    "setting_3": float,      # Operational setting 3
    "sensor_1": float,       # Sensor measurement 1
    # ... sensors 2-21
    "RUL": int,              # Remaining useful life (target)
})
```

---

## Processed Data

### Aggregated Demand

Hourly demand by location:

```python
pd.DataFrame({
    "location_id": str,      # Location identifier
    "timestamp": pd.Timestamp,  # Hour start
    "demand": float,         # Number of trips
    "hour": int,             # Hour of day (0-23)
    "day_of_week": int,      # Day of week (0-6)
    "month": int,            # Month (1-12)
    "is_weekend": bool,      # Weekend flag
})
```

**Schema:**

| Column | Type | Description |
|--------|------|-------------|
| location_id | string | Location identifier |
| timestamp | datetime | Hour start |
| demand | float | Trip count |
| hour | int | 0-23 |
| day_of_week | int | 0=Mon, 6=Sun |
| month | int | 1-12 |
| is_weekend | bool | True if Sat/Sun |

### Fleet State

Current vehicle positions and status:

```python
pd.DataFrame({
    "vehicle_id": str,       # Unique vehicle ID
    "current_location": str, # Current location
    "capacity": int,         # Passenger capacity
    "status": str,           # operational, maintenance, downtime
    "mileage_km": float,     # Total mileage
    "service_due_days": int, # Days until service
})
```

**Status Values:**

| Status | Description |
|--------|-------------|
| operational | Available for service |
| maintenance | Scheduled maintenance |
| downtime | Out of service |

### Network Costs

Zone-to-zone cost matrix:

```python
# As DataFrame
pd.DataFrame({
    "zone_1": [0, 10, 25, ...],
    "zone_2": [10, 0, 15, ...],
    "zone_3": [25, 15, 0, ...],
}, index=["zone_1", "zone_2", "zone_3"])

# As NumPy array
np.array([
    [0, 10, 25],
    [10, 0, 15],
    [25, 15, 0]
])
```

---

## Model Artifacts

### Forecast Model

XGBoost model saved with metadata:

```
data/models/demand_forecast/
├── model.json          # XGBoost model
├── metadata.json       # Training metadata
└── feature_names.json  # Feature column names
```

**metadata.json:**

```json
{
  "model_type": "xgboost",
  "version": "1.0.0",
  "trained_at": "2024-01-15T10:30:00Z",
  "training_data": {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "num_samples": 100000
  },
  "metrics": {
    "rmse": 5.2,
    "mae": 3.8,
    "mape": 0.12
  },
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 5,
    "learning_rate": 0.1
  }
}
```

---

## API Data Formats

### Demand Forecast

```json
{
  "1": [15, 18, 22, 25, 28, 24, 20],
  "2": [10, 12, 14, 16, 18, 15, 12],
  "3": [8, 9, 11, 13, 15, 12, 10]
}
```

- Keys: Location IDs (string)
- Values: Hourly demand arrays (floats)

### Fleet State (API)

```json
{
  "vehicles": [
    {
      "id": "V001",
      "location": 1,
      "capacity": 1,
      "status": "operational"
    }
  ]
}
```

### Allocation Plan

```json
{
  "allocation_plan": [
    {
      "vehicle_id": "V001",
      "source_location": 1,
      "target_location": 2,
      "cost": 15.5,
      "assignment": "rebalance"
    }
  ],
  "total_cost": 245.50,
  "kpis": {
    "demand_coverage": 0.96,
    "utilization": 0.78,
    "rebalanced_count": 12
  }
}
```

### Risk Scores

```json
{
  "risk_scores": [
    {
      "vehicle_id": "V001",
      "risk_score": 0.45,
      "risk_category": "medium",
      "factors": {
        "age_contribution": 0.15,
        "utilization_contribution": 0.20,
        "maintenance_contribution": 0.10
      }
    }
  ]
}
```

---

## Data Validation

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import Dict, List

class DemandForecast(BaseModel):
    forecasts: Dict[str, List[float]]

    @validator('forecasts')
    def validate_non_negative(cls, v):
        for loc, values in v.items():
            if any(x < 0 for x in values):
                raise ValueError(f"Demand must be non-negative")
        return v

class Vehicle(BaseModel):
    id: str = Field(..., min_length=1)
    location: int = Field(..., ge=1)
    capacity: int = Field(default=1, ge=1)
    status: str = Field(default="operational")
```

---

## File Naming Conventions

### Processed Data

```
data/processed/
├── demand/
│   ├── demand_2023.parquet
│   └── demand_2024.parquet
├── fleet_state/
│   ├── fleet_state.parquet
│   └── network_costs.npy
└── features/
    └── features_2023.parquet
```

### Model Artifacts

```
data/models/
├── demand_forecast/
│   ├── v1/
│   │   ├── model.json
│   │   └── metadata.json
│   └── v2/
│       ├── model.json
│       └── metadata.json
└── risk_scoring/
    └── v1/
        ├── model.pkl
        └── metadata.json
```

## Next Steps

- [Constraints](constraints.md) - Constraint definitions
- [Configuration](configuration.md) - Config options
