"""Baseline comparison, chronological backtesting, and recursive forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from demand_inventory.evaluation import forecast_metrics
from demand_inventory.features import FEATURE_COLUMNS, build_features

MODEL_NAMES = ("naive", "seasonal_naive", "moving_average_7", "hist_gradient_boosting")


def _baseline(name: str, history: list[float]) -> float:
    if not history:
        return 0.0
    if name == "naive":
        return history[-1]
    if name == "seasonal_naive":
        return history[-7] if len(history) >= 7 else float(np.mean(history))
    if name == "moving_average_7":
        return float(np.mean(history[-7:]))
    raise ValueError(f"Unknown baseline model: {name}")


def _future_feature_row(history: list[float], date: pd.Timestamp) -> dict[str, float]:
    values: dict[str, float] = {}
    for lag in (1, 7, 14, 28):
        values[f"lag_{lag}"] = history[-lag] if len(history) >= lag else float(np.mean(history))
    for window in (7, 14, 28):
        values[f"rolling_mean_{window}"] = float(np.mean(history[-window:]))
    values.update(
        day_of_week=float(date.dayofweek),
        month=float(date.month),
        day_of_year=float(date.dayofyear),
    )
    return values


def _fit_tree(training: pd.DataFrame) -> HistGradientBoostingRegressor | None:
    features = build_features(training).dropna(subset=FEATURE_COLUMNS)
    if features.empty:
        return None
    return HistGradientBoostingRegressor(
        max_iter=100, max_leaf_nodes=15, learning_rate=0.08,
        l2_regularization=1.0, random_state=17,
    ).fit(features[FEATURE_COLUMNS], features["demand"])


def backtest(
    panel: pd.DataFrame,
    test_days: int = 28,
    model_names: tuple[str, ...] = MODEL_NAMES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate models on each SKU's final contiguous time window."""
    if test_days < 1:
        raise ValueError("test_days must be at least 1.")
    if not model_names or set(model_names) - set(MODEL_NAMES):
        raise ValueError(f"model_names must be selected from {MODEL_NAMES}")
    predictions: list[pd.DataFrame] = []
    scores: list[dict[str, object]] = []
    for sku_id, series in panel.sort_values("date").groupby("sku_id"):
        series = series.sort_values("date").reset_index(drop=True)
        if len(series) <= test_days:
            raise ValueError(f"SKU {sku_id} needs more than {test_days} daily observations.")
        cutoff = len(series) - test_days
        history = series.loc[:cutoff - 1, "demand"].astype(float).tolist()
        actual = series.loc[cutoff:, "demand"].to_numpy(dtype=float)
        dates = series.loc[cutoff:, "date"].to_numpy()
        for name in model_names:
            model = _fit_tree(series.iloc[:cutoff]) if name == "hist_gradient_boosting" else None
            recursive = history.copy()
            values = []
            for date in dates:
                if name == "hist_gradient_boosting" and model is not None:
                    value = float(model.predict(pd.DataFrame([_future_feature_row(recursive, pd.Timestamp(date))]))[0])
                else:
                    value = _baseline(name, recursive)
                value = max(0.0, value)
                values.append(value)
                recursive.append(value)
            forecast = np.asarray(values)
            predictions.append(pd.DataFrame(
                {"sku_id": sku_id, "date": dates, "actual": actual,
                 "forecast": forecast, "model": name}
            ))
            scores.append({"sku_id": sku_id, "model": name, **forecast_metrics(actual, forecast)})
    prediction_frame = pd.concat(predictions, ignore_index=True)
    score_frame = pd.DataFrame(scores)
    aggregate = [
        {"sku_id": "ALL", "model": name, **forecast_metrics(group["actual"], group["forecast"])}
        for name, group in prediction_frame.groupby("model")
    ]
    return prediction_frame, pd.concat([score_frame, pd.DataFrame(aggregate)], ignore_index=True)


def forecast_future(
    panel: pd.DataFrame,
    horizon: int = 30,
    model_name: str = "moving_average_7",
) -> pd.DataFrame:
    if horizon < 1:
        raise ValueError("horizon must be at least 1.")
    if model_name not in MODEL_NAMES:
        raise ValueError(f"model_name must be one of {MODEL_NAMES}")
    forecasts = []
    for sku_id, series in panel.sort_values("date").groupby("sku_id"):
        series = series.sort_values("date")
        history = series["demand"].astype(float).tolist()
        model = _fit_tree(series) if model_name == "hist_gradient_boosting" else None
        dates = pd.date_range(series["date"].max() + pd.Timedelta(days=1), periods=horizon, freq="D")
        values = []
        for date in dates:
            value = (
                float(model.predict(pd.DataFrame([_future_feature_row(history, date)]))[0])
                if model is not None else _baseline(model_name, history)
            )
            value = max(0.0, value)
            values.append(value)
            history.append(value)
        forecasts.append(pd.DataFrame({"sku_id": sku_id, "date": dates, "forecast": values}))
    return pd.concat(forecasts, ignore_index=True)
