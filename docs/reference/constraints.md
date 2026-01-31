# Constraints Reference

Complete reference for operational constraints.

## Overview

Constraints are defined in `config/constraints/fleet_constraints.json` and control optimization behavior.

---

## Constraint Categories

### Capacity Constraints

Control fleet size and distribution:

```json
{
  "capacity_constraints": {
    "max_vehicles_per_location": 20,
    "min_vehicles_per_location": 2,
    "total_fleet_size": 50
  }
}
```

| Constraint | Type | Description |
|------------|------|-------------|
| `max_vehicles_per_location` | int | Maximum vehicles at any location |
| `min_vehicles_per_location` | int | Minimum vehicles at any location |
| `total_fleet_size` | int | Total fleet constraint |

### Operational Constraints

Control operational parameters:

```json
{
  "operational_constraints": {
    "max_rebalancing_distance_km": 100,
    "max_daily_trips_per_vehicle": 10,
    "max_trip_duration_minutes": 60,
    "vehicle_capacity": 1
  }
}
```

| Constraint | Type | Description |
|------------|------|-------------|
| `max_rebalancing_distance_km` | float | Max distance for vehicle movement |
| `max_daily_trips_per_vehicle` | int | Max trips per day |
| `max_trip_duration_minutes` | int | Max single trip duration |
| `vehicle_capacity` | int | Passengers per vehicle |

### Service Level Constraints

Control service quality:

```json
{
  "service_level_constraints": {
    "min_demand_coverage": 0.95,
    "max_wait_time_minutes": 15,
    "min_utilization": 0.6,
    "max_utilization": 0.9
  }
}
```

| Constraint | Type | Description |
|------------|------|-------------|
| `min_demand_coverage` | float | Minimum demand served (0-1) |
| `max_wait_time_minutes` | int | Maximum customer wait |
| `min_utilization` | float | Minimum fleet utilization |
| `max_utilization` | float | Maximum fleet utilization |

### Cost Constraints

Control costs:

```json
{
  "cost_constraints": {
    "max_rebalancing_cost_per_day": 10000,
    "cost_per_km": 0.5,
    "cost_per_minute": 0.25
  }
}
```

| Constraint | Type | Description |
|------------|------|-------------|
| `max_rebalancing_cost_per_day` | float | Daily cost limit |
| `cost_per_km` | float | Cost per kilometer |
| `cost_per_minute` | float | Cost per minute |

---

## Location-Specific Constraints

Override global constraints for specific locations:

```json
{
  "location_specific_constraints": {
    "zone_1": {
      "max_vehicles": 10,
      "min_vehicles": 2,
      "priority": "high"
    },
    "zone_2": {
      "max_vehicles": 15,
      "min_vehicles": 3,
      "priority": "medium"
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `max_vehicles` | int | Location max vehicles |
| `min_vehicles` | int | Location min vehicles |
| `priority` | string | Service priority level |

---

## Vehicle-Specific Constraints

Constraints for individual vehicles:

```json
{
  "vehicle_specific_constraints": {
    "V001": {
      "max_mileage_km": 50000,
      "service_due_days": 30,
      "allowed_zones": [1, 2, 3]
    },
    "V002": {
      "max_mileage_km": 60000,
      "service_due_days": 45,
      "excluded_zones": [5]
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `max_mileage_km` | int | Maximum total mileage |
| `service_due_days` | int | Days until service required |
| `allowed_zones` | list[int] | Zones vehicle can operate in |
| `excluded_zones` | list[int] | Zones vehicle cannot operate in |

---

## Time-Based Constraints

Vary constraints by time period:

```json
{
  "time_based_constraints": {
    "peak_hours": {
      "hours": [7, 8, 9, 17, 18, 19],
      "min_demand_coverage": 0.98,
      "max_wait_time_minutes": 10
    },
    "off_peak": {
      "hours": [0, 1, 2, 3, 4, 5, 22, 23],
      "min_demand_coverage": 0.85,
      "max_wait_time_minutes": 20
    }
  }
}
```

---

## Full Example

Complete constraint file:

```json
{
  "global_constraints": {
    "max_vehicle_capacity": 1,
    "max_travel_distance_km": 100,
    "min_service_level_percentage": 0.95
  },

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
  },

  "location_specific_constraints": {
    "zone_1": {
      "max_vehicles": 10,
      "min_vehicles": 2
    },
    "zone_2": {
      "max_vehicles": 15,
      "min_vehicles": 3
    }
  },

  "vehicle_specific_constraints": {
    "vehicle_A1": {
      "max_mileage_km": 50000,
      "service_due_days": 30
    }
  }
}
```

---

## Constraint Types in Optimization

### Hard Constraints

Must be satisfied:

- `total_fleet_size` - Cannot exceed
- `max_vehicles_per_location` - Cannot exceed
- `min_vehicles_per_location` - Must meet

### Soft Constraints

Penalized if violated:

- `min_demand_coverage` - Penalty for unmet demand
- `max_rebalancing_cost` - Penalty for over budget

---

## Using Constraints in API

Pass constraints in optimization request:

```python
request = {
    "demand_forecast": {...},
    "fleet_state": {...},
    "constraints": {
        "max_distance": 100,
        "min_service_level": 0.95,
        "max_cost": 10000
    }
}

response = httpx.post("/api/v1/optimize", json=request)
```

---

## Constraint Validation

Constraints are validated at startup:

```python
def validate_constraints(constraints: dict) -> bool:
    """Validate constraint consistency."""
    # Check total capacity
    min_total = sum(c.get('min_vehicles', 0)
                    for c in constraints.get('location_specific', {}).values())
    max_total = constraints.get('capacity', {}).get('total_fleet_size', float('inf'))

    if min_total > max_total:
        raise ValueError("Min vehicles exceed total fleet size")

    # Check service level bounds
    service_level = constraints.get('service_level', {}).get('min_demand_coverage', 0)
    if not 0 <= service_level <= 1:
        raise ValueError("Service level must be between 0 and 1")

    return True
```

## Next Steps

- [Configuration](configuration.md) - Config options
- [Data Formats](data-formats.md) - Data schemas
- [Changelog](changelog.md) - Version history
