import numpy as np
import pytest

from demand_inventory.data import generate_demo_data
from demand_inventory.inventory import (
    economic_order_quantity, optimize_inventory, reorder_point, safety_stock,
)
from demand_inventory.pipeline import daily_demand
from demand_inventory.service import run_project


def test_inventory_formula_examples():
    assert safety_stock(4, 9, 2) == 24
    assert reorder_point(20, 5, 30) == 130
    assert economic_order_quantity(1000, 40, 2) == pytest.approx(200)


def test_optimizer_preserves_skus_and_nonnegative_orders():
    sales, products = generate_demo_data(periods=70)
    panel = daily_demand(sales, products)
    forecast = panel.groupby("sku_id", as_index=False)["demand"].mean().rename(columns={"demand": "forecast"})
    decisions = optimize_inventory(panel, products, forecast, service_level=0.95)
    assert set(decisions["sku_id"]) == set(products["sku_id"])
    assert decisions["recommended_order"].ge(0).all()
    assert decisions["abc_xyz"].str.len().eq(2).all()


def test_end_to_end_service_outputs_decisions_and_scores():
    result = run_project(horizon=7, test_days=7)
    assert len(result["forecast"]) == 8 * 7
    assert "ALL" in result["metrics"]["sku_id"].values
    assert np.isfinite(result["decisions"]["reorder_point"]).all()
