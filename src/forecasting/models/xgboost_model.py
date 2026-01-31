"""
XGBoost demand forecasting model.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


logger = logging.getLogger(__name__)


class DemandForecaster:
    """XGBoost-based demand forecasting model."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
        **kwargs,
    ):
        """
        Initialize demand forecaster.

        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
            subsample: Row subsampling ratio
            colsample_bytree: Column subsampling ratio
            random_state: Random seed
            **kwargs: Additional XGBoost parameters
        """
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "random_state": random_state,
            "n_jobs": -1,
            **kwargs,
        }
        self.model: Optional[xgb.XGBRegressor] = None
        self.feature_names: List[str] = []
        self.metrics: Dict[str, float] = {}

    def train(
        self,
        X_train: pd.DataFrame | np.ndarray,
        y_train: pd.Series | np.ndarray,
        X_val: Optional[pd.DataFrame | np.ndarray] = None,
        y_val: Optional[pd.Series | np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        Train the demand forecasting model.

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            feature_names: Names of feature columns

        Returns:
            Dictionary of training metrics
        """
        logger.info("Training demand forecasting model...")

        self.model = xgb.XGBRegressor(**self.params)

        if feature_names:
            self.feature_names = feature_names
        elif isinstance(X_train, pd.DataFrame):
            self.feature_names = X_train.columns.tolist()

        eval_set = [(X_val, y_val)] if X_val is not None and y_val is not None else None

        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)

        # Calculate metrics on validation set
        if X_val is not None and y_val is not None:
            y_pred = self.model.predict(X_val)
            self.metrics = self._calculate_metrics(y_val, y_pred)
            logger.info(f"Validation RMSE: {self.metrics['rmse']:.2f}")
            logger.info(f"Validation R²: {self.metrics['r2']:.3f}")

        return self.metrics

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Generate demand predictions.

        Args:
            X: Features

        Returns:
            Predicted demand values
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        predictions = self.model.predict(X)
        return np.maximum(predictions, 0)  # Demand can't be negative

    def predict_by_zone(
        self,
        hour: int,
        day_of_week: int,
        month: int,
        zone_ids: List[int],
        historical_demand: Optional[Dict[int, float]] = None,
    ) -> Dict[int, float]:
        """
        Predict demand for multiple zones.

        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Mon)
            month: Month (1-12)
            zone_ids: List of zone IDs
            historical_demand: Optional dict of zone_id -> last demand

        Returns:
            Dictionary of zone_id -> predicted demand
        """
        is_weekend = 1 if day_of_week >= 5 else 0

        predictions = {}
        for zone_id in zone_ids:
            # Build feature vector
            features = {
                "hour": hour,
                "day_of_week": day_of_week,
                "month": month,
                "is_weekend": is_weekend,
                "zone_id": zone_id,
            }

            # Add lag features if available
            if historical_demand and zone_id in historical_demand:
                features["demand_lag_1"] = historical_demand[zone_id]
                features["demand_lag_24"] = historical_demand.get(zone_id, 0)
                features["demand_rolling_mean_24"] = historical_demand.get(zone_id, 0)
            else:
                features["demand_lag_1"] = 10  # Default
                features["demand_lag_24"] = 10
                features["demand_rolling_mean_24"] = 10

            X = pd.DataFrame([features])[self.feature_names]
            predictions[zone_id] = float(self.predict(X)[0])

        return predictions

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance.

        Returns:
            DataFrame with feature importances
        """
        if self.model is None:
            raise ValueError("Model not trained.")

        importance_df = pd.DataFrame(
            {"feature": self.feature_names, "importance": self.model.feature_importances_}
        ).sort_values("importance", ascending=False)

        return importance_df

    def save(self, path: Path | str) -> None:
        """
        Save model to disk.

        Args:
            path: Directory to save model
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save model
        self.model.save_model(path / "model.json")

        # Save metadata
        metadata = {
            "params": self.params,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
        }
        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Model saved to {path}")

    @classmethod
    def load(cls, path: Path | str) -> "DemandForecaster":
        """
        Load model from disk.

        Args:
            path: Directory containing saved model

        Returns:
            Loaded DemandForecaster instance
        """
        path = Path(path)

        # Load metadata
        with open(path / "metadata.json") as f:
            metadata = json.load(f)

        # Create instance
        forecaster = cls(**metadata["params"])
        forecaster.feature_names = metadata["feature_names"]
        forecaster.metrics = metadata["metrics"]

        # Load model
        forecaster.model = xgb.XGBRegressor()
        forecaster.model.load_model(path / "model.json")

        logger.info(f"Model loaded from {path}")
        return forecaster

    @staticmethod
    def _calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate regression metrics."""
        return {
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "r2": float(r2_score(y_true, y_pred)),
            "mape": float(np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100),
        }
