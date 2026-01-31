# Troubleshooting Guide

Common issues and solutions for the Fleet Decision Platform.

## Quick Diagnostics

```bash
# Check service health
curl http://localhost:8000/health

# Check logs for errors
grep "ERROR" logs/fleet_cascade.log | tail -20

# Check system resources
top -p $(pgrep -f uvicorn)

# Check port availability
lsof -i :8000
```

---

## Common Issues

### Installation Issues

??? question "uv command not found"

    **Cause:** uv is not installed or not in PATH.

    **Solution:**
    ```bash
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH
    export PATH="$HOME/.cargo/bin:$PATH"

    # Verify
    uv --version
    ```

??? question "Python version mismatch"

    **Cause:** Wrong Python version installed.

    **Solution:**
    ```bash
    # Check version
    python --version

    # Install correct version (macOS)
    brew install python@3.12

    # Use specific version with uv
    uv sync --python 3.12
    ```

??? question "Dependency resolution failed"

    **Cause:** Conflicting package versions.

    **Solution:**
    ```bash
    # Clear cache and reinstall
    rm -rf .venv uv.lock
    uv sync
    ```

---

### Startup Issues

??? question "Port 8000 already in use"

    **Cause:** Another process is using the port.

    **Solution:**
    ```bash
    # Find process using port
    lsof -i :8000

    # Kill the process
    kill -9 <PID>

    # Or use different port
    uvicorn src.api.main:app --port 8001
    ```

??? question "Configuration file not found"

    **Cause:** Missing or misplaced config file.

    **Solution:**
    ```bash
    # Check file exists
    ls -la config/config.yaml

    # Create from template
    cp config/config.example.yaml config/config.yaml
    ```

??? question "Environment variables not loaded"

    **Cause:** Missing .env file or incorrect format.

    **Solution:**
    ```bash
    # Create .env file
    cp .env.example .env

    # Verify contents
    cat .env

    # Test loading
    python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('APP_PORT'))"
    ```

---

### API Issues

??? question "500 Internal Server Error"

    **Cause:** Unhandled exception in application.

    **Solution:**
    ```bash
    # Check logs for traceback
    tail -100 logs/fleet_cascade.log | grep -A 10 "ERROR"

    # Enable debug mode for more details
    LOG_LEVEL=DEBUG make run
    ```

??? question "422 Validation Error"

    **Cause:** Invalid request body.

    **Solution:**
    ```bash
    # Check request format against schema
    curl http://localhost:8000/docs

    # Example valid request
    curl -X POST http://localhost:8000/api/v1/optimize \
      -H "Content-Type: application/json" \
      -d '{"demand_forecast": {"1": [10]}, "fleet_state": {"vehicles": []}, "constraints": {}}'
    ```

??? question "Timeout on optimization requests"

    **Cause:** Optimization taking too long.

    **Solution:**
    ```yaml
    # Increase timeout in config
    optimization:
      solver_settings:
        time_limit_seconds: 120  # Increase from 60
        optimality_gap: 0.05    # Allow larger gap
    ```

---

### Optimization Issues

??? question "Infeasible optimization problem"

    **Cause:** Constraints cannot be satisfied.

    **Solution:**
    ```python
    # Check constraint feasibility
    total_supply = sum(vehicles)
    total_demand = sum(demand_forecast)

    if total_supply < total_demand * min_service_level:
        print("Not enough vehicles to meet service level")

    # Relax constraints
    constraints = {
        "min_service_level": 0.8,  # Lower from 0.95
        "max_distance": 150         # Increase from 100
    }
    ```

??? question "Suboptimal solutions"

    **Cause:** Solver time limit or gap tolerance too strict.

    **Solution:**
    ```yaml
    # Adjust solver settings
    optimization:
      solver_settings:
        time_limit_seconds: 300  # More time
        optimality_gap: 0.01     # Tighter gap
    ```

??? question "Optimization is very slow"

    **Cause:** Large problem size or inefficient formulation.

    **Solution:**
    ```python
    # Reduce problem size
    # - Aggregate locations
    # - Reduce time horizon
    # - Simplify constraints

    # Or use faster solver
    optimization:
      solver: "ortools"  # Generally faster than PuLP
    ```

---

### Data Issues

??? question "Kaggle download fails"

    **Cause:** Invalid or expired API credentials.

    **Solution:**
    ```bash
    # Verify credentials
    cat ~/.kaggle/kaggle.json

    # Or set environment variables
    export KAGGLE_USERNAME=your_username
    export KAGGLE_KEY=your_api_key

    # Test connection
    kaggle datasets list -s test
    ```

??? question "Model file not found"

    **Cause:** Model not trained or wrong path.

    **Solution:**
    ```bash
    # Check model directory
    ls -la data/models/

    # Train model if missing
    uv run python scripts/train_models.py
    ```

??? question "Data type errors"

    **Cause:** Unexpected data format.

    **Solution:**
    ```python
    # Validate data before processing
    import pandas as pd

    df = pd.read_parquet("data/processed/demand.parquet")
    print(df.dtypes)
    print(df.head())

    # Convert types if needed
    df['demand'] = df['demand'].astype(float)
    ```

---

### Database Issues

??? question "Cannot connect to PostgreSQL"

    **Cause:** Database not running or wrong credentials.

    **Solution:**
    ```bash
    # Check if PostgreSQL is running
    pg_isready -h localhost -p 5432

    # Test connection
    psql -h localhost -U fleet_user -d fleet_db -c "SELECT 1"

    # Check environment variables
    echo $POSTGRES_HOST $POSTGRES_PORT $POSTGRES_USER
    ```

??? question "Redis connection refused"

    **Cause:** Redis not running.

    **Solution:**
    ```bash
    # Start Redis
    docker run -d -p 6379:6379 redis:7-alpine

    # Or check if already running
    redis-cli ping
    # Should return: PONG
    ```

---

## Debugging Techniques

### Enable Debug Logging

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Or in config
logging:
  level: "DEBUG"
```

### Interactive Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb (install first)
import ipdb; ipdb.set_trace()
```

### Profile Performance

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = optimizer.optimize(...)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)
```

---

## Getting Help

1. **Check Logs:** `tail -f logs/fleet_cascade.log`
2. **Search Issues:** [GitHub Issues](https://github.com/yourusername/fleet-cascade/issues)
3. **Ask Community:** [GitHub Discussions](https://github.com/yourusername/fleet-cascade/discussions)
4. **Documentation:** Review relevant guides

## Next Steps

- [Monitoring](monitoring.md) - Set up observability
- [Deployment](deployment.md) - Production deployment
