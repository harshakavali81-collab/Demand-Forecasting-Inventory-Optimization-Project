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
    data_source = st.radio("Data source", ["Synthetic demo", "Upload CSV files"])
    st.header("Planning assumptions")
    horizon = st.slider("Forecast horizon (days)", 7, 90, 30, step=1)
    service_level = st.select_slider("Target service level", options=[0.90, 0.95, 0.975, 0.99], value=0.95)
    days_cover = st.slider("Target days of supply", 14, 90, 45)
    forecast_model = st.selectbox(
        "Forecast model",
        ["moving_average_7", "naive", "seasonal_naive", "hist_gradient_boosting"],
    )

sales_input = None
products_input = None
if data_source == "Upload CSV files":
    sales_file = st.file_uploader("Sales transactions CSV", type=["csv"])
    products_file = st.file_uploader("Products and supplier assumptions CSV", type=["csv"])
    if sales_file is None or products_file is None:
        st.info("Upload both CSV files to generate forecasts from your data.")
        st.stop()
    try:
        sales_input = pd.read_csv(sales_file)
        products_input = pd.read_csv(products_file)
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        st.error(f"Unable to read the uploaded CSV files: {exc}")
        st.stop()


@st.cache_data(ttl="15m", max_entries=8)
def load_results(
    horizon_days: int, target_service: float, supply_days: int, model_name: str,
    sales_frame: pd.DataFrame | None, products_frame: pd.DataFrame | None,
):
    return run_project(
        horizon=horizon_days, service_level=target_service,
        max_days_of_supply=supply_days, forecast_model=model_name,
        sales=sales_frame, products=products_frame,
    )


try:
    with st.spinner("Validating data, evaluating forecasts, and calculating stock policies..."):
        results = load_results(
            horizon, service_level, days_cover, forecast_model, sales_input, products_input
        )
except (ValueError, KeyError) as exc:
    st.error(f"Could not run the planning workflow: {exc}")
    st.stop()

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

tab_overview, tab_eda, tab_forecast, tab_inventory, tab_models = st.tabs(
    ["Overview", "Demand exploration", "Forecast", "Inventory decisions", "Model evaluation"]
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

with tab_eda:
    st.subheader("SKU demand profile")
    summary = results["sku_summary"].sort_values("total_units", ascending=False)
    st.dataframe(summary, hide_index=True)
    eda_left, eda_right = st.columns(2)
    with eda_left:
        st.markdown("**Historical demand by category**")
        st.bar_chart(results["category_summary"], x="category", y="total_units")
    with eda_right:
        st.markdown("**Daily units by weekday**")
        weekday = results["demand"].assign(
            day_of_week=results["demand"]["date"].dt.day_name()
        ).groupby("day_of_week", as_index=False)["demand"].mean()
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday["sort"] = weekday["day_of_week"].map({day: i for i, day in enumerate(weekday_order)})
        st.bar_chart(weekday.sort_values("sort"), x="day_of_week", y="demand")

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
