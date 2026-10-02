"""Lagged demand features built strictly from prior observations."""

from __future__ import annotations

import pandas as pd

FEATURE_COLUMNS = [
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "day_of_week", "month", "day_of_year",
]


def build_features(demand: pd.DataFrame) -> pd.DataFrame:
    required = {"sku_id", "date", "demand"}
    missing = required - set(demand.columns)
    if missing:
        raise ValueError(f"Demand panel is missing columns: {sorted(missing)}")
    frame = demand.sort_values(["sku_id", "date"]).copy()
    grouped = frame.groupby("sku_id", sort=False)["demand"]
    for lag in (1, 7, 14, 28):
        frame[f"lag_{lag}"] = grouped.shift(lag)
    prior = frame.groupby("sku_id", sort=False)["demand"].shift(1)
    for window in (7, 14, 28):
        frame[f"rolling_mean_{window}"] = prior.groupby(
            frame["sku_id"], sort=False
        ).rolling(window, min_periods=window).mean().reset_index(level=0, drop=True)
    frame["day_of_week"] = frame["date"].dt.dayofweek
    frame["month"] = frame["date"].dt.month
    frame["day_of_year"] = frame["date"].dt.dayofyear
    return frame
