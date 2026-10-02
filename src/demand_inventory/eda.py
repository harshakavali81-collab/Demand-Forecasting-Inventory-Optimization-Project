"""Exploratory summaries for daily SKU demand."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sku_demand_summary(panel: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Summarize volume, variability, intermittency, and calendar span by SKU."""
    summary = panel.groupby("sku_id").agg(
        observed_days=("date", "nunique"),
        total_units=("demand", "sum"),
        mean_daily_demand=("demand", "mean"),
        std_daily_demand=("demand", "std"),
        zero_demand_days=("demand", lambda values: int(values.eq(0).sum())),
    ).reset_index()
    summary["std_daily_demand"] = summary["std_daily_demand"].fillna(0.0)
    summary["coefficient_of_variation"] = np.where(
        summary["mean_daily_demand"] > 0,
        summary["std_daily_demand"] / summary["mean_daily_demand"],
        np.inf,
    )
    summary["zero_demand_pct"] = np.where(
        summary["observed_days"] > 0,
        summary["zero_demand_days"] / summary["observed_days"],
        0.0,
    )
    return summary.merge(products[["sku_id", "product_name", "category"]], on="sku_id", how="left")


def category_demand_summary(panel: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Aggregate historical SKU-day units by category."""
    return (
        panel.merge(products[["sku_id", "category"]], on="sku_id", how="left")
        .groupby("category", as_index=False)
        .agg(total_units=("demand", "sum"), mean_daily_units=("demand", "mean"))
        .sort_values("total_units", ascending=False)
        .reset_index(drop=True)
    )
