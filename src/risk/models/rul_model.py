"""
Risk prediction model for Remaining Useful Life (RUL).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

from src.utils.config import get_config, get_config_value


logger = logging.getLogger(__name__)


class RULPredictor:
    """
    Remaining Useful Life prediction model.

    Predicts how many cycles/time units until asset failure
    based on sensor readings and operational data.
    """

    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        rul_cap: int = 125,
        random_state: int = 42,
        **kwargs,
    ):
        """
        Initialize RUL predictor.

        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
            rul_cap: Maximum RUL value (piece-wise linear)
            random_state: Random seed
            **kwargs: Additional XGBoost parameters
        """
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": random_state,
            "n_jobs": -1,
            **kwargs,
        }
        self.rul_cap = rul_cap
        self.model: Optional[xgb.XGBRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.metrics: Dict[str, float] = {}

    def train(
        self,
        X_train: pd.DataFrame | np.ndarray,
        y_train: pd.Series | np.ndarray,
        X_val: Optional[pd.DataFrame | np.ndarray] = None,
        y_val: Optional[pd.Series | np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
        scale_features: bool = True,
    ) -> Dict[str, float]:
        """
        Train RUL prediction model.

        Args:
            X_train: Training features
            y_train: Training RUL values
            X_val: Validation features
            y_val: Validation RUL values
            feature_names: Feature column names
            scale_features: Whether to standardize features

        Returns:
            Dictionary of training metrics
        """
        logger.info("Training RUL prediction model...")

        if feature_names:
            self.feature_names = feature_names
        elif isinstance(X_train, pd.DataFrame):
            self.feature_names = X_train.columns.tolist()

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
        else:
            X_train_scaled = X_train

        # Clip RUL
        y_train_clipped = np.clip(y_train, 0, self.rul_cap)
        y_val_clipped = np.clip(y_val, 0, self.rul_cap) if y_val is not None else None

        # Train model
        self.model = xgb.XGBRegressor(**self.params)
        self.model.fit(X_train_scaled, y_train_clipped, verbose=False)

        # Evaluate
        if X_val is not None and y_val is not None:
            y_pred = self.predict(X_val)
            self.metrics = self._calculate_metrics(y_val_clipped, y_pred)
            logger.info(f"Validation RMSE: {self.metrics['rmse']:.2f} cycles")
            logger.info(f"Validation R²: {self.metrics['r2']:.3f}")

        return self.metrics

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Predict Remaining Useful Life.

        Args:
            X: Features (sensor readings)

        Returns:
            Predicted RUL values
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X

        predictions = self.model.predict(X_scaled)
        return np.clip(predictions, 0, self.rul_cap)

    def predict_risk_score(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Convert RUL prediction to risk score (0-1).

        Higher score = higher risk (lower RUL).

        Args:
            X: Features

        Returns:
            Risk scores (0-1)
        """
        rul = self.predict(X)
        # Normalize: low RUL = high risk
        risk_score = 1 - (rul / self.rul_cap)
        return np.clip(risk_score, 0, 1)

    def categorize_risk(
        self, X: pd.DataFrame | np.ndarray, thresholds: Dict[str, float] = None
    ) -> List[str]:
        """
        Categorize assets by risk level.

        Args:
            X: Features
            thresholds: Risk score thresholds for categories

        Returns:
            List of risk categories
        """
        if thresholds is None:
            thresholds = get_config_value(
                get_config(), "risk.thresholds", {"high": 0.7, "medium": 0.4, "low": 0.0}
            )

        risk_scores = self.predict_risk_score(X)
        categories = []

        for score in risk_scores:
            if score >= thresholds["high"]:
                categories.append("high")
            elif score >= thresholds["medium"]:
                categories.append("medium")
            else:
                categories.append("low")

        return categories

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance."""
        if self.model is None:
            raise ValueError("Model not trained.")

        return pd.DataFrame(
            {"feature": self.feature_names, "importance": self.model.feature_importances_}
        ).sort_values("importance", ascending=False)

    def save(self, path: Path | str) -> None:
        """Save model to disk."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save model
        self.model.save_model(path / "model.json")

        # Save scaler
        if self.scaler is not None:
            np.save(path / "scaler_mean.npy", self.scaler.mean_)
            np.save(path / "scaler_scale.npy", self.scaler.scale_)

        # Save metadata
        metadata = {
            "params": self.params,
            "rul_cap": self.rul_cap,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "has_scaler": self.scaler is not None,
        }
        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"RUL model saved to {path}")

    @classmethod
    def load(cls, path: Path | str) -> "RULPredictor":
        """Load model from disk."""
        path = Path(path)

        with open(path / "metadata.json") as f:
            metadata = json.load(f)

        predictor = cls(rul_cap=metadata["rul_cap"], **metadata["params"])
        predictor.feature_names = metadata["feature_names"]
        predictor.metrics = metadata["metrics"]

        # Load model
        predictor.model = xgb.XGBRegressor()
        predictor.model.load_model(path / "model.json")

        # Load scaler
        if metadata.get("has_scaler"):
            predictor.scaler = StandardScaler()
            predictor.scaler.mean_ = np.load(path / "scaler_mean.npy")
            predictor.scaler.scale_ = np.load(path / "scaler_scale.npy")

        logger.info(f"RUL model loaded from {path}")
        return predictor

    @staticmethod
    def _calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate regression metrics."""
        return {
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "r2": float(r2_score(y_true, y_pred)),
        }


def calculate_heuristic_risk(
    fleet_df: pd.DataFrame, weights: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Calculate heuristic risk scores for fleet vehicles.

    Simple risk model based on age, mileage, and maintenance status.

    Args:
        fleet_df: Fleet state with columns: age_months, mileage_km, status
        weights: Weights for each factor

    Returns:
        DataFrame with risk_score and risk_category columns
    """
    if weights is None:
        weights = get_config_value(
            get_config(), "risk.heuristic_weights", {"age": 0.3, "mileage": 0.4, "maintenance": 0.3}
        )

    df = fleet_df.copy()

    # Normalize factors (0-1)
    if "age_months" in df.columns:
        df["age_norm"] = df["age_months"] / df["age_months"].max()
    else:
        df["age_norm"] = 0.5

    if "mileage_km" in df.columns:
        df["mileage_norm"] = df["mileage_km"] / df["mileage_km"].max()
    else:
        df["mileage_norm"] = 0.5

    df["maintenance_norm"] = (df["status"] == "maintenance").astype(float)

    # Calculate risk score
    df["risk_score"] = (
        (
            weights["age"] * df["age_norm"]
            + weights["mileage"] * df["mileage_norm"]
            + weights["maintenance"] * df["maintenance_norm"]
        )
        .clip(0, 1)
        .round(3)
    )

    # Categorize
    df["risk_category"] = pd.cut(
        df["risk_score"], bins=[0, 0.4, 0.7, 1.0], labels=["low", "medium", "high"]
    )

    # Cleanup
    df = df.drop(columns=["age_norm", "mileage_norm", "maintenance_norm"], errors="ignore")

    return df
