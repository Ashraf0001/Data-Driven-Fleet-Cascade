# Request/Response Models

Pydantic schemas for API data validation.

## Common Models

### BaseResponse

All API responses extend this base model:

```python
class BaseResponse(BaseModel):
    status: Literal["success", "error"]
    data: Optional[Any] = None
    errors: Optional[List[ErrorDetail]] = None
    metadata: ResponseMetadata
```

### ErrorDetail

```python
class ErrorDetail(BaseModel):
    code: str           # Error code (e.g., "VALIDATION_ERROR")
    message: str        # Human-readable message
    field: Optional[str] = None  # Field that caused error
    detail: Optional[str] = None # Additional details
```

### ResponseMetadata

```python
class ResponseMetadata(BaseModel):
    timestamp: datetime
    version: str = "0.1.0"
    request_id: Optional[str] = None
```

---

## Optimization Models

### OptimizationRequest

```python
class OptimizationRequest(BaseModel):
    demand_forecast: Dict[str, List[float]]
    fleet_state: FleetState
    constraints: OptimizationConstraints
    options: Optional[OptimizationOptions] = None

    class Config:
        json_schema_extra = {
            "example": {
                "demand_forecast": {
                    "1": [15, 18, 22, 25],
                    "2": [10, 12, 14, 16]
                },
                "fleet_state": {
                    "vehicles": [
                        {"id": "V001", "location": 1, "capacity": 1}
                    ]
                },
                "constraints": {
                    "max_distance": 100,
                    "min_service_level": 0.95
                }
            }
        }
```

### FleetState

```python
class Vehicle(BaseModel):
    id: str
    location: int
    capacity: int = 1
    status: Literal["operational", "maintenance", "downtime"] = "operational"

class FleetState(BaseModel):
    vehicles: List[Vehicle]
```

### OptimizationConstraints

```python
class OptimizationConstraints(BaseModel):
    max_distance: float = 100.0
    min_service_level: float = 0.95
    max_rebalancing_cost: Optional[float] = None
    capacity_per_vehicle: int = 1
```

### OptimizationResponse

```python
class AllocationItem(BaseModel):
    vehicle_id: str
    source_location: int
    target_location: int
    cost: float
    assignment: Literal["stay", "rebalance", "maintenance"]

class OptimizationKPIs(BaseModel):
    demand_coverage: float
    utilization: float
    rebalanced_count: int
    total_distance: float

class OptimizationResult(BaseModel):
    allocation_plan: List[AllocationItem]
    total_cost: float
    kpis: OptimizationKPIs
    solver_status: str

class OptimizationResponse(BaseResponse):
    data: Optional[OptimizationResult] = None
```

---

## Forecasting Models

### ForecastRequest

```python
class ForecastRequest(BaseModel):
    location_ids: List[int]
    horizon_hours: int = 168  # 7 days
    features: Optional[ForecastFeatures] = None

class ForecastFeatures(BaseModel):
    start_date: Optional[date] = None
    include_intervals: bool = False
    confidence_level: float = 0.95
```

### ForecastResponse

```python
class ForecastMetadata(BaseModel):
    model: str
    horizon_hours: int
    generated_at: datetime

class ForecastResult(BaseModel):
    forecasts: Dict[str, List[float]]
    intervals: Optional[Dict[str, Dict[str, List[float]]]] = None
    metadata: ForecastMetadata

class ForecastResponse(BaseResponse):
    data: Optional[ForecastResult] = None
```

---

## Risk Models

### RiskScoreRequest

```python
class VehicleRiskInput(BaseModel):
    id: str
    age_days: int
    utilization_rate: float
    days_since_maintenance: int

class RiskScoreRequest(BaseModel):
    vehicles: List[VehicleRiskInput]
```

### RiskScoreResponse

```python
class RiskFactors(BaseModel):
    age_contribution: float
    utilization_contribution: float
    maintenance_contribution: float

class VehicleRiskScore(BaseModel):
    vehicle_id: str
    risk_score: float
    risk_category: Literal["low", "medium", "high"]
    factors: RiskFactors

class RiskScoreResult(BaseModel):
    risk_scores: List[VehicleRiskScore]

class RiskScoreResponse(BaseResponse):
    data: Optional[RiskScoreResult] = None
```

---

## Data Models

### LocationModel

```python
class Location(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    avg_demand: Optional[float] = None
    max_capacity: Optional[int] = None
```

### FleetSummary

```python
class FleetSummary(BaseModel):
    total_vehicles: int
    operational: int
    maintenance: int
    downtime: int
    avg_utilization: float
    avg_risk_score: float
```

---

## Validation Rules

### Demand Forecast

```python
@validator('demand_forecast')
def validate_demand(cls, v):
    for location_id, values in v.items():
        if not all(x >= 0 for x in values):
            raise ValueError(f"Demand values must be non-negative")
        if len(values) == 0:
            raise ValueError(f"Demand array cannot be empty")
    return v
```

### Constraints

```python
@validator('min_service_level')
def validate_service_level(cls, v):
    if not 0 <= v <= 1:
        raise ValueError("Service level must be between 0 and 1")
    return v

@validator('max_distance')
def validate_distance(cls, v):
    if v <= 0:
        raise ValueError("Max distance must be positive")
    return v
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
