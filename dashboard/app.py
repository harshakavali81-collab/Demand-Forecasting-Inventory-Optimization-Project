"""Interactive demand planning dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import streamlit as st

from demand_inventory.service import run_project

st.set_page_config(page_title="Demand & Inventory Planner", page_icon="📦", layout="wide")
st.title("Demand Forecasting & Inventory Optimization")
st.caption("Synthetic portfolio demo. Review assumptions and recommendations before operational use.")

with st.sidebar:
    st.header("Planning assumptions")
    horizon = st.slider("Forecast horizon (days)", 7, 90, 30, step=1)
    service_level = st.select_slider("Target service level", options=[0.90, 0.95, 0.975, 0.99], value=0.95)
    days_cover = st.slider("Target days of supply", 14, 90, 45)
    forecast_model = st.selectbox(
        "Forecast model",
        ["moving_average_7", "naive", "seasonal_naive", "hist_gradient_boosting"],
    )


@st.cache_data(ttl="15m", max_entries=8)
def load_results(horizon_days: int, target_service: float, supply_days: int, model_name: str):
    return run_project(
        horizon=horizon_days, service_level=target_service,
        max_days_of_supply=supply_days, forecast_model=model_name,
    )


with st.spinner("Preparing demo demand, comparing forecasts, and calculating stock policies..."):
    results = load_results(horizon, service_level, days_cover, forecast_model)

decisions = results["decisions"]
forecast = results["forecast"]
metrics = results["metrics"]
aggregate_metrics = metrics.loc[metrics["sku_id"] == "ALL"].sort_values("wape", na_position="last")
selected_metrics = aggregate_metrics.loc[aggregate_metrics["model"] == forecast_model]
selected_metrics = selected_metrics.iloc[0] if not selected_metrics.empty else aggregate_metrics.iloc[0]

with st.container(horizontal=True):
    st.metric("SKUs", f"{len(decisions):,}", border=True)
    st.metric("Forecast horizon demand", f"{forecast['forecast'].sum():,.0f} units", border=True)
    st.metric("Reorder recommendations", f"{(decisions['recommended_order'] > 0).sum()}", border=True)
    st.metric("Selected model", forecast_model, border=True)
    wape = selected_metrics["wape"]
    st.metric("Holdout WAPE", "N/A" if pd.isna(wape) else f"{wape:.1%}", border=True)

tab_overview, tab_forecast, tab_inventory, tab_models = st.tabs(
    ["Overview", "Forecast", "Inventory decisions", "Model evaluation"]
)

with tab_overview:
    col_left, col_right = st.columns(2)
    daily_total = results["demand"].groupby("date", as_index=False)["demand"].sum()
    with col_left:
        st.subheader("Historical daily demand")
        st.line_chart(daily_total, x="date", y="demand")
    with col_right:
        st.subheader("Inventory status")
        status_counts = decisions.groupby("inventory_status", as_index=False)["sku_id"].count()
        st.bar_chart(status_counts, x="inventory_status", y="sku_id")
    category_summary = decisions.groupby("category", as_index=False).agg(
        skus=("sku_id", "count"), order_units=("recommended_order", "sum")
    )
    st.subheader("Recommended replenishment by category")
    st.bar_chart(category_summary, x="category", y="order_units")

with tab_forecast:
    selected = st.selectbox("Select SKU", sorted(forecast["sku_id"].unique()))
    history = results["demand"].query("sku_id == @selected").tail(90).rename(columns={"demand": "units"})
    future = forecast.query("sku_id == @selected").rename(columns={"forecast": "units"})
    chart_data = pd.concat(
        [history[["date", "units"]], future[["date", "units"]]], ignore_index=True
    )
    st.line_chart(chart_data, x="date", y="units")
    st.dataframe(future, hide_index=True)

with tab_inventory:
    categories = ["All"] + sorted(decisions["category"].unique().tolist())
    category = st.selectbox("Category filter", categories)
    risks = ["All"] + sorted(decisions["stockout_risk"].unique().tolist())
    risk = st.selectbox("Stockout risk filter", risks)
    shown = decisions.copy()
    if category != "All":
        shown = shown[shown["category"] == category]
    if risk != "All":
        shown = shown[shown["stockout_risk"] == risk]
    columns = [
        "sku_id", "product_name", "category", "current_stock", "horizon_forecast",
        "mean_daily_demand", "days_of_supply", "safety_stock", "reorder_point",
        "eoq", "recommended_order", "stockout_risk", "inventory_status", "abc_xyz",
    ]
    st.dataframe(shown[columns], hide_index=True)
    st.download_button(
        "Download recommendations CSV", shown[columns].to_csv(index=False),
        file_name="inventory_recommendations.csv", mime="text/csv",
    )

with tab_models:
    st.caption("One chronological 28-day holdout per SKU; aggregate metrics are across all held-out SKU-days.")
    st.dataframe(aggregate_metrics, hide_index=True)
    st.bar_chart(aggregate_metrics.set_index("model")[["mae", "rmse"]])

st.divider()
st.caption("Demo values are synthetic and should not be treated as actual purchasing advice.")
