import pandas as pd
import pytest

from demand_inventory.data import generate_demo_data
from demand_inventory.pipeline import clean_sales, daily_demand


def test_demo_data_creates_complete_sku_day_panel():
    sales, products = generate_demo_data(periods=40)
    panel = daily_demand(sales, products)
    assert len(panel) == 40 * len(products)
    assert panel["demand"].ge(0).all()


def test_cleaning_deduplicates_unknown_skus_and_keeps_returns():
    sales, products = generate_demo_data(periods=40)
    sales.loc[0, "quantity"] = -2
    sales.loc[1, "sku_id"] = "UNKNOWN"
    sales.loc[2, "order_id"] = sales.loc[3, "order_id"]
    cleaned = clean_sales(sales, products)
    assert cleaned["quantity"].lt(0).any()
    assert "UNKNOWN" not in cleaned["sku_id"].values
    assert not cleaned["order_id"].duplicated().any()


def test_empty_cleaned_sales_reports_invalid_input():
    sales, products = generate_demo_data(periods=40)
    sales["sku_id"] = "UNKNOWN"
    with pytest.raises(ValueError, match="No valid sales rows"):
        clean_sales(sales, products)


def test_invalid_holding_cost_is_rejected():
    sales, products = generate_demo_data(periods=40)
    products.loc[0, "annual_holding_cost"] = 0
    with pytest.raises(ValueError, match="annual_holding_cost"):
        daily_demand(sales, products)
