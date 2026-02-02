"""
Integration tests for Fleet Decision Platform API.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Fleet Decision Platform"
        assert "endpoints" in data

    def test_config_endpoint(self, client):
        """Test config endpoint returns configuration."""
        response = client.get("/api/v1/config")
        assert response.status_code == 200
        data = response.json()
        assert "forecasting" in data
        assert "optimization" in data
        assert "risk" in data
        assert "thresholds" in data["risk"]
        assert "max_cost_per_vehicle" in data["optimization"]
        assert "min_service_level" in data["optimization"]


class TestOptimizationEndpoints:
    """Test optimization endpoints."""

    def test_optimize_fleet(self, client):
        """Test basic fleet optimization."""
        request_data = {
            "demand_forecast": {"0": [10], "1": [15], "2": [8]},
            "fleet_state": {
                "vehicles": [
                    {"vehicle_id": "V001", "current_zone": 0, "status": "operational"},
                    {"vehicle_id": "V002", "current_zone": 1, "status": "operational"},
                    {"vehicle_id": "V003", "current_zone": 2, "status": "operational"},
                ]
            },
            "constraints": {"max_cost_per_vehicle": 50},
        }

        response = client.post("/api/v1/optimize", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["optimal", "infeasible"]
        assert "total_cost" in data
        assert "allocations" in data
        assert "kpis" in data

    def test_optimize_simulation(self, client):
        """Test optimization with simulated data."""
        response = client.post("/api/v1/optimize/simulate", params={"n_vehicles": 10, "n_zones": 9})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["optimal", "infeasible"]


class TestForecastEndpoints:
    """Test forecasting endpoints."""

    def test_forecast_demand(self, client):
        """Test demand forecasting."""
        request_data = {
            "zone_ids": [0, 1, 2],
            "hour": 18,
            "day_of_week": 4,
            "month": 6,
            "horizon_hours": 1,
        }

        response = client.post("/api/v1/forecast", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "forecasts" in data
        assert "metadata" in data

    def test_forecast_empty_zones(self, client):
        """Test forecast with empty zone list."""
        request_data = {
            "zone_ids": [],
            "hour": 10,
            "day_of_week": 2,
            "month": 3,
            "horizon_hours": 1,
        }

        response = client.post("/api/v1/forecast", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["forecasts"] == {}

    def test_get_zones(self, client):
        """Test get available zones."""
        response = client.get("/api/v1/forecast/zones")
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data


class TestRiskEndpoints:
    """Test risk scoring endpoints."""

    def test_risk_scoring(self, client):
        """Test risk score calculation."""
        request_data = {
            "vehicles": [
                {
                    "vehicle_id": "V001",
                    "current_zone": 0,
                    "status": "operational",
                    "mileage_km": 50000,
                    "age_months": 24,
                },
                {
                    "vehicle_id": "V002",
                    "current_zone": 1,
                    "status": "maintenance",
                    "mileage_km": 90000,
                    "age_months": 48,
                },
            ]
        }

        response = client.post("/api/v1/risk/score", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["risk_scores"]) == 2
        assert "summary" in data

    def test_risk_thresholds(self, client):
        """Test risk thresholds endpoint."""
        response = client.get("/api/v1/risk/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert "thresholds" in data
        assert "factors" in data
