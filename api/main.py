"""FastAPI interface to the illustrative demand/inventory demo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi import FastAPI, HTTPException, Query

from demand_inventory.forecasting import MODEL_NAMES
from demand_inventory.service import run_project

app = FastAPI(
    title="Demand Forecasting & Inventory Optimization API",
    version="1.0.0",
    description="Illustrative synthetic-data endpoints; not live purchasing advice.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data": "synthetic demo"}


@app.get("/decisions")
def decisions(
    horizon: int = Query(default=30, ge=7, le=90),
    service_level: float = Query(default=0.95, gt=0.5, lt=1),
    max_days_of_supply: int = Query(default=45, ge=1, le=180),
    model: str = Query(default="moving_average_7"),
) -> dict[str, object]:
    if model not in MODEL_NAMES:
        raise HTTPException(status_code=422, detail=f"model must be one of {MODEL_NAMES}")
    try:
        result = run_project(
            horizon=horizon, service_level=service_level,
            max_days_of_supply=max_days_of_supply, forecast_model=model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    selected_forecast = result["forecast"]
    decisions_frame = result["decisions"]
    return {
        "notice": "Synthetic portfolio demonstration. Validate all assumptions before use.",
        "forecast_horizon_days": horizon,
        "model_evaluation": result["metrics"].query("sku_id == 'ALL'").to_dict(orient="records"),
        "forecast": selected_forecast.to_dict(orient="records"),
        "inventory_decisions": decisions_frame.to_dict(orient="records"),
    }
