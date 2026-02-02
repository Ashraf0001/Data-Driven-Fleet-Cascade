# Installation

This guide covers detailed installation instructions for the Fleet Decision Platform.

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| CPU | 2 cores |
| RAM | 4 GB |
| Storage | 10 GB |
| OS | macOS, Linux, Windows (WSL2) |

### Recommended for Production

| Component | Requirement |
|-----------|-------------|
| CPU | 8+ cores |
| RAM | 16+ GB |
| Storage | 100+ GB SSD |
| OS | Ubuntu 22.04 LTS |

## Step 1: Install Prerequisites

=== "macOS"

    ```bash
    # Install Homebrew (if not installed)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Install Python and uv
    brew install python@3.12
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install PostgreSQL (optional)
    brew install postgresql@15
    ```

=== "Ubuntu/Debian"

    ```bash
    # Update system
    sudo apt update && sudo apt upgrade -y

    # Install Python
    sudo apt install python3.12 python3.12-venv python3-pip -y

    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install PostgreSQL (optional)
    sudo apt install postgresql postgresql-contrib -y
    ```

=== "Windows (WSL2)"

    ```powershell
    # Install WSL2 (in PowerShell as Admin)
    wsl --install -d Ubuntu-22.04

    # Then follow Ubuntu instructions inside WSL
    ```

## Step 2: Clone Repository

```bash
# Clone via HTTPS
git clone https://github.com/Ashraf0001/Data-Driven-Fleet-Cascade.git

# Or clone via SSH
git clone git@github.com:Ashraf0001/Data-Driven-Fleet-Cascade.git

# Navigate to project
cd Data-Driven-Fleet-Cascade
```

## Step 3: Install Dependencies

```bash
# Install production dependencies
uv sync

# Verify installation
uv run python -c "import src; print(f'Version: {src.__version__}')"
```

### Optional: Install Development Dependencies

```bash
# Install all optional dependencies
uv sync --all-extras

# Set up pre-commit hooks
uv run pre-commit install
```

## Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `KAGGLE_USERNAME` | Kaggle API username | For data download |
| `KAGGLE_KEY` | Kaggle API key | For data download |
| `POSTGRES_*` | Database credentials | Phase 2+ |

## Step 5: Verify Installation

```bash
# Run health check
uv run python -c "
from src.utils.config import load_config
config = load_config()
print('✓ Configuration loaded')
print(f'  Forecasting model: {config[\"forecasting\"][\"model\"]}')
print(f'  Optimization solver: {config[\"optimization\"][\"solver\"]}')
"

# Run tests
uv run pytest tests/ -v --tb=short
```

## Troubleshooting

??? question "uv command not found"

    Ensure uv is in your PATH:
    ```bash
    export PATH="$HOME/.cargo/bin:$PATH"
    ```
    Add this to your `~/.bashrc` or `~/.zshrc`.

??? question "Python version mismatch"

    Check your Python version:
    ```bash
    python --version  # Should be 3.9+
    ```
    If needed, install Python 3.12 and set as default.

??? question "Permission denied errors"

    Ensure you have write access to the project directory:
    ```bash
    sudo chown -R $USER:$USER /path/to/Data-Driven-Fleet-Cascade
    ```

## Next Steps

- [Quick Start Guide](quickstart.md) - Run your first optimization
- [Configuration Guide](configuration.md) - Customize settings
- [Download Data](quickstart.md#download-data) - Get sample datasets
