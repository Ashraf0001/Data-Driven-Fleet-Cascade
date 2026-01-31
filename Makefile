# Fleet Decision Platform - Makefile
# Common development tasks

.PHONY: help install install-dev test lint format run download clean docs docker-build docker-run docker-down docker-push

# Default target
help:
	@echo "Fleet Decision Platform - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install all dependencies (including dev)"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make lint         Lint code with ruff"
	@echo "  make format       Format code with ruff"
	@echo "  make run          Run API server (development)"
	@echo "  make streamlit    Run Streamlit dashboard"
	@echo "  make demo         Run API + Dashboard together"
	@echo ""
	@echo "Data & Training:"
	@echo "  make download     Download datasets from Kaggle"
	@echo "  make train        Train models"
	@echo "  make pipeline     Run full optimization pipeline"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build Build Docker images"
	@echo "  make docker-run   Run containers locally"
	@echo "  make docker-down  Stop and remove containers"
	@echo "  make docker-push  Push images to DockerHub"
	@echo "  make docker-logs  View container logs"
	@echo "  make docker-clean Remove containers and images"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs         Serve documentation locally"
	@echo "  make docs-build   Build documentation"
	@echo ""
	@echo "Cleanup:"
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

streamlit:
	uv run streamlit run app.py --server.port 8501

demo:
	@echo "Starting API server and Streamlit dashboard..."
	@echo "API: http://localhost:8000/docs"
	@echo "Dashboard: http://localhost:8501"
	@(uv run uvicorn src.api.main:app --reload --port 8000 &) && sleep 2 && uv run streamlit run app.py

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
# Docker
# =============================================================================

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d
	@echo ""
	@echo "Services started:"
	@echo "  API:       http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo "  Dashboard: http://localhost:8501"
	@echo ""
	@echo "Run 'make docker-logs' to view logs"
	@echo "Run 'make docker-down' to stop services"

docker-up: docker-run

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-push:
	@echo "Pushing images to DockerHub..."
	@if [ -z "$$DOCKERHUB_USERNAME" ]; then \
		if [ -f .env ]; then \
			export $$(grep -v '^#' .env | xargs) && \
			echo "Logging in as $$DOCKERHUB_USERNAME..." && \
			echo "$$DOCKERHUB_TOKEN" | docker login -u "$$DOCKERHUB_USERNAME" --password-stdin && \
			docker-compose push; \
		else \
			echo "Error: Set DOCKERHUB_USERNAME in .env or environment"; \
			exit 1; \
		fi; \
	else \
		echo "Logging in as $$DOCKERHUB_USERNAME..." && \
		echo "$$DOCKERHUB_TOKEN" | docker login -u "$$DOCKERHUB_USERNAME" --password-stdin && \
		docker-compose push; \
	fi

docker-clean:
	docker-compose down -v --rmi local
	@echo "Removed containers, volumes, and local images"

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
