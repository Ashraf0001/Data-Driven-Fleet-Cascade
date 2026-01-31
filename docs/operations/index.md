# Operations Guide

Guide for deploying, monitoring, and maintaining the Fleet Decision Platform.

## Overview

This guide covers:

- **Deployment** - How to deploy the platform
- **Monitoring** - Observability and alerting
- **Troubleshooting** - Common issues and solutions

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Deployment__

    ---

    Deploy to production environments.

    [:octicons-arrow-right-24: Deployment](deployment.md)

-   :material-monitor:{ .lg .middle } __Monitoring__

    ---

    Monitor health and performance.

    [:octicons-arrow-right-24: Monitoring](monitoring.md)

-   :material-wrench:{ .lg .middle } __Troubleshooting__

    ---

    Diagnose and resolve issues.

    [:octicons-arrow-right-24: Troubleshooting](troubleshooting.md)

</div>

## Quick Reference

### Health Check

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
# Follow application logs
tail -f logs/fleet_cascade.log

# Filter error logs
grep "ERROR" logs/fleet_cascade.log
```

### Restart Services

```bash
# Restart API server
make restart

# Restart with clean state
make clean-restart
```

## Environment Checklist

### Development

- [ ] Python 3.9+ installed
- [ ] `uv` package manager
- [ ] Pre-commit hooks installed
- [ ] Local configuration (`.env`)

### Staging

- [ ] Docker/containers set up
- [ ] PostgreSQL database
- [ ] Redis cache (optional)
- [ ] Environment variables configured

### Production

- [ ] Load balancer configured
- [ ] SSL/TLS certificates
- [ ] Database backups
- [ ] Monitoring and alerting
- [ ] Log aggregation
- [ ] Auto-scaling (optional)

## System Requirements

### Minimum (Development)

| Component | Requirement |
|-----------|-------------|
| CPU | 2 cores |
| RAM | 4 GB |
| Storage | 10 GB |

### Recommended (Production)

| Component | Requirement |
|-----------|-------------|
| CPU | 8+ cores |
| RAM | 16+ GB |
| Storage | 100+ GB SSD |
| Network | 1 Gbps |

## Next Steps

- [Deployment Guide](deployment.md) - Production deployment
- [Monitoring Guide](monitoring.md) - Set up observability
- [Troubleshooting](troubleshooting.md) - Resolve issues
