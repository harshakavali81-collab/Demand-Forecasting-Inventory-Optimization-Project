"""Orchestration for reproducible local and application workflows."""

from __future__ import annotations

import pandas as pd

from demand_inventory.data import generate_demo_data
from demand_inventory.eda import category_demand_summary, sku_demand_summary
from demand_inventory.forecasting import backtest, forecast_future
from demand_inventory.inventory import optimize_inventory
from demand_inventory.pipeline import clean_products, daily_demand


def run_project(
    horizon: int = 30, test_days: int = 28, service_level: float = 0.95,
    max_days_of_supply: float = 45, forecast_model: str | None = None,
    sales: pd.DataFrame | None = None, products: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    if (sales is None) != (products is None):
        raise ValueError("Provide both sales and products, or neither to use demo data.")
    if sales is None:
        sales, products = generate_demo_data()
    products = clean_products(products)
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
        "sku_summary": sku_demand_summary(panel, products),
        "category_summary": category_demand_summary(panel, products),
    }
