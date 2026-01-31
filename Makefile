# Fleet Decision Platform - Makefile
# Common development tasks

.PHONY: help install install-dev test lint format run download clean docs

# Default target
help:
	@echo "Fleet Decision Platform - Available commands:"
	@echo ""
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install all dependencies (including dev)"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make lint         Lint code with ruff"
	@echo "  make format       Format code with ruff"
	@echo "  make run          Run API server (development)"
	@echo "  make download     Download datasets from Kaggle"
	@echo "  make train        Train models"
	@echo "  make pipeline     Run full optimization pipeline"
	@echo "  make docs         Serve documentation locally"
	@echo "  make clean        Clean up generated files"
	@echo ""

# =============================================================================
# Installation
# =============================================================================

install:
	uv sync

install-dev:
	uv sync --all-extras
	uv run pre-commit install

# =============================================================================
# Testing
# =============================================================================

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	uv run pytest tests/unit/ -v -m unit

test-integration:
	uv run pytest tests/integration/ -v -m integration

# =============================================================================
# Code Quality
# =============================================================================

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

# =============================================================================
# Running
# =============================================================================

run:
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# =============================================================================
# Data & Training
# =============================================================================

download:
	uv run python scripts/download_data.py

generate-fleet:
	uv run python scripts/generate_fleet.py

train:
	uv run python scripts/train_models.py

pipeline:
	uv run python scripts/run_pipeline.py

# =============================================================================
# Documentation
# =============================================================================

docs:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build

# =============================================================================
# Database (PostgreSQL)
# =============================================================================

db-init:
	psql -h localhost -U $${POSTGRES_USER:-fleet_user} -d $${POSTGRES_DB:-fleet_db} -f scripts/schema.sql

db-shell:
	psql -h localhost -U $${POSTGRES_USER:-fleet_user} -d $${POSTGRES_DB:-fleet_db}

# =============================================================================
# Cleanup
# =============================================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf build/ dist/ site/ 2>/dev/null || true

clean-data:
	rm -rf data/processed/* data/models/* data/outputs/* 2>/dev/null || true
	@echo "Cleaned processed data, models, and outputs"

# =============================================================================
# Development Helpers
# =============================================================================

check: lint test
	@echo "All checks passed!"

pre-commit:
	uv run pre-commit run --all-files
