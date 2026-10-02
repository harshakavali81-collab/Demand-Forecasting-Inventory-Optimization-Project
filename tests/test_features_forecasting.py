import numpy as np
import pandas as pd

from demand_inventory.evaluation import forecast_metrics
from demand_inventory.features import build_features
from demand_inventory.forecasting import backtest, forecast_future


def sample_panel(days=70):
    dates = pd.date_range("2025-01-01", periods=days)
    return pd.DataFrame({
        "sku_id": "A",
        "date": dates,
        "demand": np.arange(days, dtype=float) % 10 + 1,
    })


def test_lag_and_rolling_features_use_only_prior_values():
    features = build_features(sample_panel())
    assert np.isnan(features.loc[0, "lag_1"])
    assert features.loc[28, "lag_28"] == features.loc[0, "demand"]
    assert features.loc[7, "rolling_mean_7"] == features.loc[:6, "demand"].mean()


def test_backtest_is_chronological_and_future_forecast_has_nonnegative_horizon():
    panel = sample_panel()
    predictions, scores = backtest(panel, test_days=10)
    assert predictions["date"].min() == panel["date"].iloc[-10]
    assert set(scores["model"]) == {"naive", "seasonal_naive", "moving_average_7", "hist_gradient_boosting"}
    forecast = forecast_future(panel, horizon=14, model_name="hist_gradient_boosting")
    assert len(forecast) == 14
    assert forecast["forecast"].ge(0).all()


def test_metrics_zero_demand_has_undefined_wape():
    metrics = forecast_metrics(np.array([0, 0]), np.array([1, 2]))
    assert metrics["mae"] == 1.5
    assert metrics["wape"] is None
