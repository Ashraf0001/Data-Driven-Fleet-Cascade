# Monitoring Guide

Set up observability for the Fleet Decision Platform.

## Monitoring Stack

| Tool | Purpose | Phase |
|------|---------|-------|
| Structured Logging | Application logs | MVP |
| Health Endpoints | Service health | MVP |
| Prometheus | Metrics collection | Phase 3 |
| Grafana | Visualization | Phase 3 |
| Sentry | Error tracking | Phase 3 |

## Health Checks

### Application Health

```bash
# Health endpoint
curl http://localhost:8000/health
# {"status": "healthy"}

# Detailed health (if implemented)
curl http://localhost:8000/health/detailed
# {
#   "status": "healthy",
#   "database": "connected",
#   "cache": "connected",
#   "models_loaded": true
# }
```

### Docker Health Check

```yaml
# docker-compose.yml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Logging

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Info log with context
logger.info(
    "Optimization completed",
    request_id="req_123",
    duration_ms=1250,
    total_cost=2450.00,
    vehicles_rebalanced=12
)

# Error log
logger.error(
    "Optimization failed",
    request_id="req_124",
    error="Infeasible constraints"
)
```

### Log Format (JSON)

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "info",
  "logger": "src.optimization.cascade",
  "event": "Optimization completed",
  "request_id": "req_123",
  "duration_ms": 1250,
  "total_cost": 2450.00,
  "vehicles_rebalanced": 12
}
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging info |
| INFO | Normal operations |
| WARNING | Recoverable issues |
| ERROR | Errors handled |
| CRITICAL | System failures |

### Log Configuration

```yaml
# config/config.yaml
logging:
  level: "INFO"
  format: "json"  # text for development

  handlers:
    console:
      enabled: true
    file:
      enabled: true
      path: "logs/fleet_cascade.log"
      rotation: "daily"
      retention: 30
```

---

## Metrics (Phase 3+)

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
optimization_requests = Counter(
    'fleet_optimization_requests_total',
    'Total optimization requests',
    ['status']
)

# Histograms
optimization_duration = Histogram(
    'fleet_optimization_duration_seconds',
    'Optimization duration',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)

# Gauges
fleet_utilization = Gauge(
    'fleet_utilization_ratio',
    'Current fleet utilization'
)
```

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `requests_total` | Counter | Total API requests |
| `request_duration_seconds` | Histogram | Request latency |
| `optimization_cost` | Histogram | Optimization cost distribution |
| `demand_coverage_ratio` | Gauge | Current demand coverage |
| `fleet_utilization_ratio` | Gauge | Fleet utilization |
| `error_total` | Counter | Total errors |

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'fleet-cascade'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

---

## Dashboards (Phase 3+)

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Fleet Decision Platform",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(fleet_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Optimization Duration P95",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, fleet_optimization_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

### Key Dashboard Panels

1. **Request Metrics**
   - Request rate (req/sec)
   - Error rate
   - P50/P95/P99 latency

2. **Business Metrics**
   - Optimizations per hour
   - Average cost savings
   - Demand coverage

3. **System Health**
   - CPU/Memory usage
   - Database connections
   - Cache hit rate

---

## Alerting

### Alert Rules

```yaml
# alerts.yml
groups:
  - name: fleet-cascade
    rules:
      - alert: HighErrorRate
        expr: rate(fleet_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"

      - alert: OptimizationTimeout
        expr: histogram_quantile(0.99, fleet_optimization_duration_seconds_bucket) > 60
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Optimization taking too long"

      - alert: LowDemandCoverage
        expr: fleet_demand_coverage_ratio < 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Demand coverage below threshold"
```

### Alert Channels

- Slack
- PagerDuty
- Email
- Webhooks

---

## Error Tracking (Phase 3+)

### Sentry Integration

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    environment="production",
    traces_sample_rate=0.1
)

# Capture error with context
with sentry_sdk.push_scope() as scope:
    scope.set_tag("module", "optimization")
    scope.set_context("request", {
        "fleet_size": 50,
        "locations": 5
    })
    sentry_sdk.capture_exception(error)
```

---

## Log Aggregation

### ELK Stack

```yaml
# docker-compose.yml (additions)
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

---

## Monitoring Checklist

- [ ] Health endpoints working
- [ ] Structured logging enabled
- [ ] Log aggregation configured
- [ ] Metrics exposed (Phase 3)
- [ ] Dashboards created (Phase 3)
- [ ] Alerts configured (Phase 3)
- [ ] Error tracking enabled (Phase 3)

## Next Steps

- [Troubleshooting](troubleshooting.md) - Resolve issues
- [Deployment](deployment.md) - Production deployment
