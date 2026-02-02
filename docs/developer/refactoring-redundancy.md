# Refactoring: Redundancy Consolidation

This note documents the redundancy cleanup performed on the refactoring branch.
The goal is to reduce duplicated generators/config defaults and align runtime behavior
with `config/config.yaml`.

## What Changed

### Generator consolidation
- Moved location metadata generation to `src/data/loader.py` and reused it in
  `scripts/generate_fleet.py`.
- Updated `scripts/generate_fleet.py` to rely on `src/data/loader.py` for fleet state
  and network costs.
- Updated `app.py` to use `src/data/loader.py` for fleet state and demand forecasts,
  replacing local ad-hoc generators.

### Config-driven defaults
- Added a cached config loader in `src/utils/config.py` to avoid repeated disk reads.
- `src/api/main.py` now serves config values from `config/config.yaml` with safe
  fallbacks if config is unavailable.
- Risk thresholds and heuristic weights now come from `config/config.yaml` in
  `src/api/routes/risk.py` and `src/risk/models/rul_model.py`.

### Feature naming alignment
- Aligned forecasting feature names in `config/config.yaml` with
  `src/data/preprocessing.py` to avoid mismatches.

## Files Updated

- `src/utils/config.py`: added cached config access.
- `config/config.yaml`: aligned feature names and risk weights; added
  `max_cost_per_vehicle` for optimization constraints.
- `src/data/loader.py`: added `generate_location_metadata`; added optional
  `status_distribution` for fleet generation.
- `scripts/generate_fleet.py`: now uses canonical generators and config defaults.
- `app.py`: uses canonical generators for fleet state and demand.
- `src/api/main.py`: returns config-driven values.
- `src/api/routes/risk.py`: uses config-driven thresholds/weights.
- `src/risk/models/rul_model.py`: uses config-driven defaults.

## Notes

- No files were deleted; this is a consolidation to reduce duplicate logic.
- `scripts/generate_fleet.py` keeps extra per-vehicle columns (utilization, maintenance)
  as script-specific augmentation.

## Follow-ups (Optional)

- Consider a shared data schema document (fleet state fields and meanings).
- Consider moving any remaining "default" values into `config/config.yaml` and
  reading them through `src/utils/config.py`.
