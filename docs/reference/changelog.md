# Changelog

All notable changes to the Fleet Decision Platform.

## [Unreleased]

### Added
- Initial project structure
- MkDocs documentation site
- Configuration management system
- Data ingestion framework
- Fleet simulation scripts

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

---

## [0.1.0] - 2024-XX-XX (MVP)

### Added

**Core Features:**
- XGBoost demand forecasting model
- Min-cost flow optimization (OR-Tools)
- Heuristic risk scoring
- Basic cost analysis
- FastAPI REST endpoints

**Data Processing:**
- NYC Taxi data ingestion
- NASA Turbofan data loading
- Fleet state simulation
- Network cost generation
- Feature engineering pipeline

**API Endpoints:**
- `POST /api/v1/optimize` - Fleet optimization
- `POST /api/v1/forecast` - Demand forecasting
- `POST /api/v1/risk/score` - Risk assessment
- `GET /health` - Health check
- `GET /api/v1/config` - Configuration

**Documentation:**
- Getting started guide
- Architecture documentation
- API reference
- User guide
- Developer guide
- Operations guide

**Infrastructure:**
- uv package management
- Pre-commit hooks (ruff)
- MkDocs documentation
- Makefile commands
- pytest test framework

### Known Limitations
- No authentication (MVP)
- No persistent database (file-based)
- Single optimization stage only
- Heuristic risk scoring only
- No caching

---

## Roadmap

### Phase 2 - Enhanced ML

**Planned:**
- [ ] Prophet forecasting model
- [ ] Hierarchical forecasting
- [ ] ML risk classification
- [ ] SHAP explainability
- [ ] Binding constraint analysis
- [ ] Redis caching
- [ ] PostgreSQL database

### Phase 3 - Contract Intelligence

**Planned:**
- [ ] PDF contract parsing
- [ ] OCR text extraction
- [ ] NLP constraint extraction
- [ ] Pinecone vector storage
- [ ] RAG-based constraint search
- [ ] Constraint registry

### Phase 4 - Production

**Planned:**
- [ ] MILP optimization refinement
- [ ] Survival analysis models
- [ ] Temporal Fusion Transformer
- [ ] Docker deployment
- [ ] AWS ECS deployment
- [ ] Full monitoring stack
- [ ] API authentication

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

---

## Migration Guides

### Upgrading to 0.2.0 (Future)

```bash
# Backup data
cp -r data/ data_backup/

# Update dependencies
uv sync

# Run migrations
uv run python scripts/migrate_to_v02.py

# Verify
uv run pytest
```

---

## Contributors

See [GitHub Contributors](https://github.com/yourusername/fleet-cascade/graphs/contributors).

---

## Links

- [GitHub Releases](https://github.com/yourusername/fleet-cascade/releases)
- [GitHub Milestones](https://github.com/yourusername/fleet-cascade/milestones)
- [GitHub Issues](https://github.com/yourusername/fleet-cascade/issues)
