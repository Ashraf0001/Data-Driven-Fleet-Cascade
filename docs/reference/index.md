# Reference Documentation

Complete reference for configuration, data formats, and constraints.

<div class="grid cards" markdown>

-   :material-cog:{ .lg .middle } __Configuration Options__

    ---

    All configuration parameters explained.

    [:octicons-arrow-right-24: Configuration](configuration.md)

-   :material-database:{ .lg .middle } __Data Formats__

    ---

    Input and output data schemas.

    [:octicons-arrow-right-24: Data Formats](data-formats.md)

-   :material-lock:{ .lg .middle } __Constraints__

    ---

    Operational constraint definitions.

    [:octicons-arrow-right-24: Constraints](constraints.md)

-   :material-history:{ .lg .middle } __Changelog__

    ---

    Version history and changes.

    [:octicons-arrow-right-24: Changelog](changelog.md)

</div>

## Quick Links

### Configuration Files

| File | Description |
|------|-------------|
| `config/config.yaml` | Main configuration |
| `config/constraints/fleet_constraints.json` | Fleet constraints |
| `.env` | Environment variables |
| `pyproject.toml` | Package configuration |

### Data Directories

| Directory | Contents |
|-----------|----------|
| `data/raw/` | Downloaded raw data |
| `data/processed/` | Cleaned/transformed data |
| `data/models/` | Trained model artifacts |
| `data/outputs/` | Generated outputs |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/optimize` | POST | Run optimization |
| `/api/v1/forecast` | POST | Generate forecasts |
| `/api/v1/risk/score` | POST | Calculate risk scores |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KAGGLE_USERNAME` | Yes* | Kaggle API username |
| `KAGGLE_KEY` | Yes* | Kaggle API key |
| `POSTGRES_HOST` | No | Database host |
| `POSTGRES_PASSWORD` | No | Database password |
| `REDIS_HOST` | No | Cache host |
| `LOG_LEVEL` | No | Logging level |

*Required for data download
