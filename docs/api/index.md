# API Reference

Complete reference for the Fleet Decision Platform REST API.

## Overview

The API provides programmatic access to all platform capabilities:

- Demand forecasting
- Fleet optimization
- Risk assessment
- Configuration management

**Base URL:** `http://localhost:8000`

**Documentation:** Interactive docs at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Authentication

!!! info "MVP: No Authentication"

    The MVP version does not require authentication. Production deployments should implement API key or JWT authentication.

## Quick Start

=== "cURL"

    ```bash
    # Health check
    curl http://localhost:8000/health

    # Get configuration
    curl http://localhost:8000/api/v1/config
    ```

=== "Python"

    ```python
    import httpx

    client = httpx.Client(base_url="http://localhost:8000")

    # Health check
    response = client.get("/health")
    print(response.json())

    # Get configuration
    response = client.get("/api/v1/config")
    print(response.json())
    ```

=== "JavaScript"

    ```javascript
    // Health check
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    console.log(data);
    ```

## API Sections

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } __Endpoints__

    ---

    Complete list of all API endpoints.

    [:octicons-arrow-right-24: View Endpoints](endpoints.md)

-   :material-code-json:{ .lg .middle } __Request/Response Models__

    ---

    Data schemas for API requests and responses.

    [:octicons-arrow-right-24: View Models](models.md)

-   :material-code-braces:{ .lg .middle } __Examples__

    ---

    Practical examples for common use cases.

    [:octicons-arrow-right-24: View Examples](examples.md)

</div>

## Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "0.1.0",
    "request_id": "req_abc123"
  }
}
```

### Error Response

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input",
      "field": "demand_forecast",
      "detail": "demand_forecast is required"
    }
  ],
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "0.1.0",
    "request_id": "req_abc123"
  }
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Rate Limiting

!!! info "MVP: No Rate Limiting"

    Rate limiting will be implemented in Phase 2 using Redis.

Future rate limits:

| Tier | Requests/Minute |
|------|-----------------|
| Default | 60 |
| Premium | 300 |
| Enterprise | Unlimited |

## Versioning

The API uses URL versioning:

- Current: `/api/v1/`
- Future: `/api/v2/` (when breaking changes are needed)

## SDKs and Libraries

!!! note "Coming Soon"

    Official SDKs for Python, JavaScript, and Go are planned for Phase 4.

## Next Steps

- [Endpoints](endpoints.md) - Detailed endpoint reference
- [Models](models.md) - Request/response schemas
- [Examples](examples.md) - Usage examples
