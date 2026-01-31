# API Examples

Practical examples for common API use cases.

## Basic Examples

### Health Check

=== "cURL"

    ```bash
    curl -s http://localhost:8000/health | jq
    ```

=== "Python"

    ```python
    import httpx

    response = httpx.get("http://localhost:8000/health")
    print(response.json())
    # {"status": "healthy"}
    ```

=== "JavaScript"

    ```javascript
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    console.log(data);
    ```

---

## Optimization Examples

### Simple Optimization

Run basic fleet optimization:

=== "cURL"

    ```bash
    curl -X POST http://localhost:8000/api/v1/optimize \
      -H "Content-Type: application/json" \
      -d '{
        "demand_forecast": {
          "1": [20, 25, 30, 35, 30, 25, 20],
          "2": [15, 18, 22, 25, 22, 18, 15],
          "3": [10, 12, 15, 18, 15, 12, 10]
        },
        "fleet_state": {
          "vehicles": [
            {"id": "V001", "location": 1, "capacity": 1},
            {"id": "V002", "location": 1, "capacity": 1},
            {"id": "V003", "location": 2, "capacity": 1},
            {"id": "V004", "location": 3, "capacity": 1},
            {"id": "V005", "location": 3, "capacity": 1}
          ]
        },
        "constraints": {
          "max_distance": 50,
          "min_service_level": 0.90
        }
      }' | jq
    ```

=== "Python"

    ```python
    import httpx

    request_data = {
        "demand_forecast": {
            "1": [20, 25, 30, 35, 30, 25, 20],
            "2": [15, 18, 22, 25, 22, 18, 15],
            "3": [10, 12, 15, 18, 15, 12, 10]
        },
        "fleet_state": {
            "vehicles": [
                {"id": "V001", "location": 1, "capacity": 1},
                {"id": "V002", "location": 1, "capacity": 1},
                {"id": "V003", "location": 2, "capacity": 1},
                {"id": "V004", "location": 3, "capacity": 1},
                {"id": "V005", "location": 3, "capacity": 1}
            ]
        },
        "constraints": {
            "max_distance": 50,
            "min_service_level": 0.90
        }
    }

    response = httpx.post(
        "http://localhost:8000/api/v1/optimize",
        json=request_data
    )

    result = response.json()
    print(f"Total Cost: ${result['data']['total_cost']:,.2f}")
    print(f"Demand Coverage: {result['data']['kpis']['demand_coverage']:.1%}")
    ```

### Process Optimization Results

```python
import pandas as pd

# Parse allocation plan
allocation_df = pd.DataFrame(result['data']['allocation_plan'])

# Filter rebalancing moves
rebalance_moves = allocation_df[allocation_df['assignment'] == 'rebalance']
print(f"\nVehicles to rebalance: {len(rebalance_moves)}")
print(rebalance_moves[['vehicle_id', 'source_location', 'target_location', 'cost']])

# Summarize by location
location_changes = allocation_df.groupby('target_location').size()
print(f"\nVehicles by target location:\n{location_changes}")
```

---

## Forecasting Examples

### Generate 7-Day Forecast

=== "cURL"

    ```bash
    curl -X POST http://localhost:8000/api/v1/forecast \
      -H "Content-Type: application/json" \
      -d '{
        "location_ids": [1, 2, 3],
        "horizon_hours": 168,
        "features": {
          "start_date": "2024-01-15",
          "include_intervals": false
        }
      }' | jq
    ```

=== "Python"

    ```python
    import httpx
    import numpy as np

    request_data = {
        "location_ids": [1, 2, 3],
        "horizon_hours": 168,
        "features": {
            "start_date": "2024-01-15",
            "include_intervals": False
        }
    }

    response = httpx.post(
        "http://localhost:8000/api/v1/forecast",
        json=request_data
    )

    result = response.json()

    # Analyze forecasts
    for location_id, forecast in result['data']['forecasts'].items():
        forecast_arr = np.array(forecast)
        print(f"\nLocation {location_id}:")
        print(f"  Mean demand: {forecast_arr.mean():.1f}")
        print(f"  Max demand: {forecast_arr.max():.1f}")
        print(f"  Peak hour: {forecast_arr.argmax()}")
    ```

---

## Risk Assessment Examples

### Calculate Fleet Risk

=== "Python"

    ```python
    import httpx

    vehicles = [
        {"id": "V001", "age_days": 180, "utilization_rate": 0.65, "days_since_maintenance": 5},
        {"id": "V002", "age_days": 900, "utilization_rate": 0.92, "days_since_maintenance": 28},
        {"id": "V003", "age_days": 450, "utilization_rate": 0.78, "days_since_maintenance": 14},
    ]

    response = httpx.post(
        "http://localhost:8000/api/v1/risk/score",
        json={"vehicles": vehicles}
    )

    result = response.json()

    # Find high-risk vehicles
    high_risk = [
        v for v in result['data']['risk_scores']
        if v['risk_category'] == 'high'
    ]

    print(f"High-risk vehicles: {len(high_risk)}")
    for v in high_risk:
        print(f"  {v['vehicle_id']}: score={v['risk_score']:.2f}")
    ```

---

## End-to-End Workflow

### Complete Pipeline

```python
import httpx

BASE_URL = "http://localhost:8000"
client = httpx.Client(base_url=BASE_URL, timeout=60.0)

# Step 1: Get current fleet state
fleet_response = client.get("/api/v1/data/fleet")
fleet_data = fleet_response.json()['data']
print(f"Fleet size: {fleet_data['summary']['total_vehicles']}")

# Step 2: Generate forecasts
forecast_response = client.post(
    "/api/v1/forecast",
    json={
        "location_ids": [1, 2, 3, 4, 5],
        "horizon_hours": 24  # Next 24 hours
    }
)
forecasts = forecast_response.json()['data']['forecasts']
print(f"Generated forecasts for {len(forecasts)} locations")

# Step 3: Calculate risk scores
vehicles_for_risk = [
    {
        "id": v['vehicle_id'],
        "age_days": 365,  # Would come from actual data
        "utilization_rate": 0.75,
        "days_since_maintenance": 10
    }
    for v in fleet_data['fleet'][:10]  # First 10 vehicles
]

risk_response = client.post(
    "/api/v1/risk/score",
    json={"vehicles": vehicles_for_risk}
)
risk_scores = risk_response.json()['data']['risk_scores']
print(f"Calculated risk for {len(risk_scores)} vehicles")

# Step 4: Run optimization
optimization_response = client.post(
    "/api/v1/optimize",
    json={
        "demand_forecast": forecasts,
        "fleet_state": {"vehicles": fleet_data['fleet']},
        "constraints": {
            "max_distance": 100,
            "min_service_level": 0.95
        }
    }
)

result = optimization_response.json()['data']
print(f"\n=== Optimization Results ===")
print(f"Total Cost: ${result['total_cost']:,.2f}")
print(f"Demand Coverage: {result['kpis']['demand_coverage']:.1%}")
print(f"Vehicles Rebalanced: {result['kpis']['rebalanced_count']}")

# Step 5: Export results
import json
with open("optimization_result.json", "w") as f:
    json.dump(result, f, indent=2)
print("\nResults saved to optimization_result.json")
```

---

## Error Handling

### Handle API Errors

```python
import httpx
from httpx import HTTPStatusError

def run_optimization(request_data):
    try:
        response = httpx.post(
            "http://localhost:8000/api/v1/optimize",
            json=request_data,
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()

    except HTTPStatusError as e:
        if e.response.status_code == 422:
            errors = e.response.json().get('errors', [])
            for error in errors:
                print(f"Validation error: {error['message']}")
                if error.get('field'):
                    print(f"  Field: {error['field']}")
        else:
            print(f"API error: {e.response.status_code}")
        return None

    except httpx.TimeoutException:
        print("Request timed out")
        return None
```

---

## Async Examples

### Async Python Client

```python
import asyncio
import httpx

async def run_optimizations(scenarios):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        tasks = [
            client.post("/api/v1/optimize", json=scenario)
            for scenario in scenarios
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Run multiple scenarios in parallel
scenarios = [
    {"demand_forecast": {...}, "fleet_state": {...}, "constraints": {...}},
    {"demand_forecast": {...}, "fleet_state": {...}, "constraints": {...}},
]

results = asyncio.run(run_optimizations(scenarios))
```

## Next Steps

- [Endpoints](endpoints.md) - Complete endpoint reference
- [Models](models.md) - Request/response schemas
- [User Guide](../user-guide/index.md) - Detailed usage guides
