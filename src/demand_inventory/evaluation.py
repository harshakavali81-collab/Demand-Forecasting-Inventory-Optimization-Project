"""Forecast metrics with explicit zero-demand behavior."""

from __future__ import annotations

import numpy as np


def forecast_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | None]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if actual.shape != predicted.shape:
        raise ValueError("Actual and predicted arrays must have the same shape.")
    if actual.size == 0:
        raise ValueError("Metrics require at least one observation.")
    errors = actual - predicted
    denominator = float(np.abs(actual).sum())
    return {
        "mae": float(np.abs(errors).mean()),
        "rmse": float(np.sqrt(np.square(errors).mean())),
        "wape": float(np.abs(errors).sum() / denominator) if denominator else None,
    }
