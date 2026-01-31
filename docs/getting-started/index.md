# Getting Started

Welcome to the Fleet Decision Platform! This guide will help you get up and running quickly.

## Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.9+ | Runtime environment |
| uv | Latest | Package management |
| Git | 2.0+ | Version control |
| PostgreSQL | 15+ | Database (optional for MVP) |

## Installation Methods

=== "Quick Install (Recommended)"

    ```bash
    # Clone and install
    git clone https://github.com/yourusername/fleet-cascade.git
    cd fleet-cascade
    uv sync
    ```

=== "Development Install"

    ```bash
    # Clone and install with dev dependencies
    git clone https://github.com/yourusername/fleet-cascade.git
    cd fleet-cascade
    uv sync --all-extras
    uv run pre-commit install
    ```

=== "Docker (Phase 4)"

    ```bash
    # Build and run with Docker
    docker-compose up -d
    ```

## What's Next?

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } __Installation__

    ---

    Detailed installation instructions for all platforms.

    [:octicons-arrow-right-24: Installation Guide](installation.md)

-   :material-rocket-launch:{ .lg .middle } __Quick Start__

    ---

    Run your first optimization in minutes.

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-cog:{ .lg .middle } __Configuration__

    ---

    Customize the platform for your needs.

    [:octicons-arrow-right-24: Configuration](configuration.md)

</div>

## Need Help?

If you run into issues:

1. Check the [Troubleshooting Guide](../operations/troubleshooting.md)
2. Search [GitHub Issues](https://github.com/yourusername/fleet-cascade/issues)
3. Ask in [Discussions](https://github.com/yourusername/fleet-cascade/discussions)
