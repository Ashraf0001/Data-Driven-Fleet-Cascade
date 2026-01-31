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
    "horizon_days": 7
  },
  "optimization": {
    "solver": "ortools",
    "stages": ["min_cost_flow"]
  },
  "features": {
    "enable_caching": true,
    "enable_risk_scoring": true
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
        "id": "V001",
        "location": 1,
        "capacity": 1,
        "status": "operational"
      }
    ]
  },
  "constraints": {
    "max_distance": 100,
    "min_service_level": 0.95
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
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
    },
    "solver_status": "optimal"
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "solve_time_ms": 1250
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
  "location_ids": [1, 2, 3],
  "horizon_hours": 168,
  "features": {
    "start_date": "2024-01-15",
    "include_intervals": false
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "forecasts": {
      "1": [15, 18, 22, 25, 28, 24, 20],
      "2": [10, 12, 14, 16, 18, 15, 12],
      "3": [8, 9, 11, 13, 15, 12, 10]
    },
    "metadata": {
      "model": "xgboost",
      "horizon_hours": 168,
      "generated_at": "2024-01-15T10:30:00Z"
    }
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
      "id": "V001",
      "age_days": 365,
      "utilization_rate": 0.75,
      "days_since_maintenance": 14
    }
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
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
}
```

---

## Data Management

### GET /api/v1/data/locations

Get location metadata.

**Response:**

```json
{
  "status": "success",
  "data": {
    "locations": [
      {
        "id": 1,
        "name": "Manhattan-Midtown",
        "latitude": 40.7580,
        "longitude": -73.9855
      }
    ]
  }
}
```

### GET /api/v1/data/fleet

Get current fleet state.

**Response:**

```json
{
  "status": "success",
  "data": {
    "fleet": [
      {
        "vehicle_id": "V001",
        "location_id": 1,
        "status": "operational",
        "capacity": 1
      }
    ],
    "summary": {
      "total_vehicles": 50,
      "operational": 43,
      "maintenance": 5,
      "downtime": 2
    }
  }
}
```

---

## WebSocket (Phase 3+)

### WS /ws/optimization

Real-time optimization updates.

**Message Types:**

```json
// Subscribe to optimization job
{"type": "subscribe", "job_id": "opt_123"}

// Progress update
{"type": "progress", "job_id": "opt_123", "progress": 0.75}

// Completion
{"type": "complete", "job_id": "opt_123", "result": {...}}
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
