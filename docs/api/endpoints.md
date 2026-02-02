# API Endpoints

Complete reference for all REST API endpoints.

## Health & Status

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

### GET /

Root endpoint with service information.

**Response:**

```json
{
  "name": "Fleet Decision Platform",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

---

## Configuration

### GET /api/v1/config

Get current platform configuration (non-sensitive values).

**Response:**

```json
{
  "forecasting": {
    "model": "xgboost",
    "horizon_days": 7,
    "features": ["hour", "day_of_week", "month", "is_weekend", "demand_lag_1"]
  },
  "optimization": {
    "solver": "ortools",
    "stages": ["min_cost_flow"],
    "max_cost_per_vehicle": 50.0,
    "min_service_level": 0.0
  },
  "risk": {
    "model": "heuristic",
    "thresholds": {"high": 0.7, "medium": 0.4, "low": 0.0}
  }
}
```

---

## Optimization

### POST /api/v1/optimize

Run the optimization pipeline.

**Request Body:**

```json
{
  "demand_forecast": {
    "1": [15, 18, 22, 25],
    "2": [10, 12, 14, 16],
    "3": [8, 9, 11, 13]
  },
  "fleet_state": {
    "vehicles": [
      {
        "vehicle_id": "V001",
        "current_zone": 1,
        "capacity": 1,
        "status": "operational"
      }
    ]
  },
  "constraints": {
    "max_cost_per_vehicle": 50,
    "min_service_level": 0.95
  }
}
```

**Response:**

```json
{
  "status": "optimal",
  "total_cost": 245.50,
  "allocations": [
    {
      "vehicle_id": "V001",
      "from_zone": 1,
      "to_zone": 2,
      "cost": 15.5,
      "rebalanced": true
    }
  ],
  "coverage": 0.8,
  "kpis": {
    "vehicles_allocated": 10,
    "vehicles_rebalanced": 3,
    "zones_served": 8,
    "total_zones": 10,
    "total_demand": 50,
    "demand_served": 10,
    "utilization": 0.75
  }
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Optimization successful |
| 400 | Invalid input data |
| 422 | Infeasible constraints |
| 500 | Optimization failed |

---

## Forecasting

### POST /api/v1/forecast

Generate demand forecasts.

**Request Body:**

```json
{
  "zone_ids": [0, 1, 2],
  "hour": 18,
  "day_of_week": 4,
  "month": 6,
  "horizon_hours": 1
}
```

**Response:**

```json
{
  "status": "success",
  "forecasts": {
    "0": [15],
    "1": [12],
    "2": [10]
  },
  "metadata": {
    "model": "heuristic"
  }
}
```

---

## Risk Assessment

### POST /api/v1/risk/score

Calculate risk scores for fleet vehicles.

**Request Body:**

```json
{
  "vehicles": [
    {
      "vehicle_id": "V001",
      "current_zone": 0,
      "status": "operational",
      "mileage_km": 50000,
      "age_months": 24
    }
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "risk_scores": [
    {
      "vehicle_id": "V001",
      "risk_score": 0.45,
      "risk_category": "medium",
      "factors": {
        "age_contribution": 0.15,
        "mileage_contribution": 0.20,
        "status_contribution": 0.10
      }
    }
  ],
  "summary": {
    "low": 10,
    "medium": 5,
    "high": 2
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid request data |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `INFEASIBLE_PROBLEM` | Optimization constraints infeasible |
| `SOLVER_ERROR` | Optimization solver failed |
| `MODEL_NOT_LOADED` | ML model not available |
| `INTERNAL_ERROR` | Unexpected server error |

## Next Steps

- [Request/Response Models](models.md) - Data schemas
- [Examples](examples.md) - Usage examples
