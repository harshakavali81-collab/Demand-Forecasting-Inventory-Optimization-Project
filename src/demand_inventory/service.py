"""Orchestration for reproducible local and application workflows."""

from __future__ import annotations

import pandas as pd

from demand_inventory.data import generate_demo_data
from demand_inventory.forecasting import backtest, forecast_future
from demand_inventory.inventory import optimize_inventory
from demand_inventory.pipeline import daily_demand


def run_project(
    horizon: int = 30, test_days: int = 28, service_level: float = 0.95,
    max_days_of_supply: float = 45, forecast_model: str | None = None,
) -> dict[str, pd.DataFrame]:
    sales, products = generate_demo_data()
    panel = daily_demand(sales, products)
    predictions, metrics = backtest(panel, test_days=test_days)
    champion = metrics.loc[metrics["sku_id"] == "ALL"].sort_values("wape", na_position="last").iloc[0]["model"]
    selected_model = forecast_model or str(champion)
    future = forecast_future(panel, horizon=horizon, model_name=selected_model)
    future["model"] = selected_model
    decisions = optimize_inventory(panel, products, future, service_level, max_days_of_supply)
    return {
        "sales": sales, "products": products, "demand": panel,
        "backtest_predictions": predictions, "metrics": metrics,
        "forecast": future, "decisions": decisions,
    }
