"""Validation, cleaning, and daily SKU demand aggregation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from demand_inventory.data import PRODUCT_COLUMNS, SALES_COLUMNS


def validate_sales(sales: pd.DataFrame) -> None:
    missing = set(SALES_COLUMNS) - set(sales.columns)
    if missing:
        raise ValueError(f"Sales data is missing required columns: {sorted(missing)}")
    if sales.empty:
        raise ValueError("Sales data must contain at least one row.")


def validate_products(products: pd.DataFrame) -> None:
    missing = set(PRODUCT_COLUMNS) - set(products.columns)
    if missing:
        raise ValueError(f"Product data is missing required columns: {sorted(missing)}")
    if products["sku_id"].duplicated().any():
        raise ValueError("Product data must contain one row per sku_id.")
    assumption_columns = [
        "unit_cost", "current_stock", "lead_time_days",
        "minimum_order_quantity", "order_cost", "annual_holding_cost",
    ]
    if (products[assumption_columns] < 0).any().any():
        raise ValueError("Product costs, stock, lead times, and order constraints cannot be negative.")


def clean_sales(sales: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate rows; preserve returns as negative quantities."""
    validate_sales(sales)
    validate_products(products)
    frame = sales.copy()
    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce")
    for column in ("quantity", "unit_price", "discount"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["discount"] = frame["discount"].fillna(0.0)
    frame = frame.drop_duplicates(subset=["order_id"])
    frame = frame.dropna(subset=["order_date", "sku_id", "quantity", "unit_price"])
    frame = frame[
        np.isfinite(frame["quantity"])
        & np.isfinite(frame["unit_price"])
        & (frame["unit_price"] >= 0)
        & frame["discount"].between(0, 1)
        & frame["sku_id"].isin(products["sku_id"])
    ]
    return frame.sort_values(["sku_id", "order_date"]).reset_index(drop=True)


def daily_demand(sales: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Produce a complete daily SKU panel; net returns against sales, floor at zero."""
    clean = clean_sales(sales, products)
    observed = clean.groupby(
        ["sku_id", clean["order_date"].dt.normalize()], as_index=False
    )["quantity"].sum().rename(columns={"order_date": "date", "quantity": "demand"})
    dates = pd.date_range(
        observed["date"].min(), observed["date"].max(), freq="D"
    )
    panel = pd.MultiIndex.from_product(
        [products["sku_id"].tolist(), dates], names=["sku_id", "date"]
    ).to_frame(index=False)
    panel = panel.merge(observed, on=["sku_id", "date"], how="left")
    panel["demand"] = panel["demand"].fillna(0).clip(lower=0).astype(float)
    return panel.sort_values(["sku_id", "date"]).reset_index(drop=True)
