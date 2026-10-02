"""Explainable inventory controls and ABC-XYZ segmentation."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm


def service_level_z(service_level: float) -> float:
    if not 0.5 < service_level < 1:
        raise ValueError("service_level must be greater than 0.5 and less than 1.")
    return float(norm.ppf(service_level))


def safety_stock(daily_demand_std: float, lead_time_days: float, z_score: float) -> float:
    if daily_demand_std < 0 or lead_time_days < 0 or z_score < 0:
        raise ValueError("Standard deviation, lead time, and z-score cannot be negative.")
    return float(z_score * daily_demand_std * math.sqrt(lead_time_days))


def reorder_point(mean_daily_demand: float, lead_time_days: float, safety_stock_units: float) -> float:
    if min(mean_daily_demand, lead_time_days, safety_stock_units) < 0:
        raise ValueError("Demand, lead time, and safety stock cannot be negative.")
    return float(mean_daily_demand * lead_time_days + safety_stock_units)


def economic_order_quantity(annual_demand: float, order_cost: float, annual_holding_cost: float) -> float:
    if min(annual_demand, order_cost, annual_holding_cost) < 0:
        raise ValueError("EOQ inputs cannot be negative.")
    if annual_holding_cost == 0:
        raise ValueError("annual_holding_cost must be greater than zero.")
    return float(math.sqrt(2 * annual_demand * order_cost / annual_holding_cost))


def abc_xyz_segments(
    panel: pd.DataFrame, products: pd.DataFrame,
    x_threshold: float = 0.5, y_threshold: float = 1.0,
) -> pd.DataFrame:
    frame = panel.merge(products[["sku_id", "unit_cost"]], on="sku_id", how="left")
    stats = frame.groupby("sku_id").agg(
        total_units=("demand", "sum"), mean_daily_demand=("demand", "mean"),
        std_daily_demand=("demand", "std"),
    ).reset_index()
    stats["std_daily_demand"] = stats["std_daily_demand"].fillna(0.0)
    stats["cv"] = np.where(
        stats["mean_daily_demand"] > 0,
        stats["std_daily_demand"] / stats["mean_daily_demand"], np.inf,
    )
    unit_cost = frame.groupby("sku_id")["unit_cost"].first()
    stats["revenue_proxy"] = stats["total_units"] * stats["sku_id"].map(unit_cost)
    stats = stats.sort_values("revenue_proxy", ascending=False).reset_index(drop=True)
    total = float(stats["revenue_proxy"].sum())
    cumulative = stats["revenue_proxy"].cumsum() / total if total > 0 else pd.Series(0.0, index=stats.index)
    stats["abc_class"] = np.select([cumulative <= 0.80, cumulative <= 0.95], ["A", "B"], default="C")
    stats["xyz_class"] = np.select(
        [stats["cv"] <= x_threshold, stats["cv"] <= y_threshold], ["X", "Y"], default="Z"
    )
    stats["abc_xyz"] = stats["abc_class"] + stats["xyz_class"]
    return stats.drop(columns="revenue_proxy")


def optimize_inventory(
    panel: pd.DataFrame, products: pd.DataFrame, forecast: pd.DataFrame,
    service_level: float = 0.95, max_days_of_supply: float = 45,
) -> pd.DataFrame:
    if max_days_of_supply <= 0:
        raise ValueError("max_days_of_supply must be greater than zero.")
    z_score = service_level_z(service_level)
    stats = panel.groupby("sku_id")["demand"].agg(
        mean_daily_demand="mean", std_daily_demand="std"
    ).fillna(0.0).reset_index()
    future = forecast.groupby("sku_id")["forecast"].sum().rename("horizon_forecast").reset_index()
    result = products.merge(stats, on="sku_id", how="left").merge(future, on="sku_id", how="left")
    result[["mean_daily_demand", "std_daily_demand", "horizon_forecast"]] = result[
        ["mean_daily_demand", "std_daily_demand", "horizon_forecast"]
    ].fillna(0.0)
    result["safety_stock"] = result.apply(
        lambda row: safety_stock(row.std_daily_demand, row.lead_time_days, z_score), axis=1
    )
    result["reorder_point"] = result.apply(
        lambda row: reorder_point(row.mean_daily_demand, row.lead_time_days, row.safety_stock), axis=1
    )
    result["eoq"] = result.apply(
        lambda row: economic_order_quantity(
            row.mean_daily_demand * 365, row.order_cost, row.annual_holding_cost
        ), axis=1
    )
    result["days_of_supply"] = np.where(
        result["mean_daily_demand"] > 0,
        result["current_stock"] / result["mean_daily_demand"], np.inf,
    )
    result["recommended_order"] = result.apply(
        lambda row: _order_quantity(row, max_days_of_supply), axis=1
    )
    result["stockout_risk"] = np.select(
        [
            result["current_stock"] <= result["mean_daily_demand"] * result["lead_time_days"],
            result["current_stock"] < result["reorder_point"],
        ], ["HIGH", "MEDIUM"], default="LOW",
    )
    result["inventory_status"] = np.select(
        [result["recommended_order"] > 0, result["days_of_supply"] > max_days_of_supply],
        ["REORDER", "OVERSTOCK"], default="HEALTHY",
    )
    segments = abc_xyz_segments(panel, products)
    return result.merge(segments[["sku_id", "abc_xyz"]], on="sku_id", how="left")


def _order_quantity(row: pd.Series, max_days_of_supply: float) -> int:
    if row.current_stock >= row.reorder_point:
        return 0
    target_stock = max(row.reorder_point, row.mean_daily_demand * max_days_of_supply)
    quantity = max(0.0, target_stock - row.current_stock)
    quantity = max(quantity, float(row.minimum_order_quantity))
    return int(math.ceil(quantity))
