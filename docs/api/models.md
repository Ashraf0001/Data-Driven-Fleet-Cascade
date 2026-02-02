# Request/Response Models

Pydantic schemas used by the API (`src/api/models/schemas.py`).

## Optimization Models

### OptimizationRequest

```python
class OptimizationRequest(BaseModel):
    demand_forecast: Dict[str, List[float]]
    fleet_state: FleetState
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints)
    network_costs: Optional[List[List[float]]] = None
```

### FleetState and Vehicle

```python
class Vehicle(BaseModel):
    vehicle_id: str
    current_zone: int
    capacity: int = 1
    status: str = "operational"
    mileage_km: Optional[float] = None
    age_months: Optional[int] = None
    risk_score: Optional[float] = None

class FleetState(BaseModel):
    vehicles: List[Vehicle]
```

### OptimizationConstraints

```python
class OptimizationConstraints(BaseModel):
    max_cost_per_vehicle: float = 50.0
    min_service_level: float = 0.0
    max_distance: Optional[float] = None
```

### OptimizationResponse

```python
class Allocation(BaseModel):
    vehicle_id: str
    from_zone: int
    to_zone: int
    cost: float
    rebalanced: bool = False

class OptimizationKPIs(BaseModel):
    vehicles_allocated: int = 0
    vehicles_rebalanced: int = 0
    zones_served: int = 0
    total_zones: int = 0
    total_demand: int = 0
    demand_served: int = 0
    utilization: float = 0.0

class OptimizationResponse(BaseModel):
    status: str
    total_cost: float
    allocations: List[Allocation]
    coverage: float
    kpis: OptimizationKPIs
```

---

## Forecasting Models

### ForecastRequest

```python
class ForecastRequest(BaseModel):
    zone_ids: List[int]
    hour: int
    day_of_week: int
    month: int
    horizon_hours: int = 1
    historical_demand: Optional[Dict[int, float]] = None
```

### ForecastResponse

```python
class ForecastResponse(BaseModel):
    status: str = "success"
    forecasts: Dict[str, List[float]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## Risk Models

### RiskScoreRequest

```python
class RiskScoreRequest(BaseModel):
    vehicles: List[Vehicle]
    use_ml_model: bool = False
```

### RiskScoreResponse

```python
class VehicleRiskScore(BaseModel):
    vehicle_id: str
    risk_score: float
    risk_category: str
    factors: Optional[Dict[str, float]] = None

class RiskScoreResponse(BaseModel):
    status: str = "success"
    risk_scores: List[VehicleRiskScore]
    summary: Dict[str, int] = Field(default_factory=dict)
```

---

## OpenAPI Schema

The full OpenAPI schema is available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **JSON Schema:** `http://localhost:8000/openapi.json`

## Next Steps

- [Endpoints](endpoints.md) - API endpoint reference
- [Examples](examples.md) - Usage examples
