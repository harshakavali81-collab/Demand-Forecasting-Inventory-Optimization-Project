"""Command-line entry point for the end-to-end demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from demand_inventory.service import run_project


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demand forecasting and inventory recommendations.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--horizon", type=int, default=30)
    parser.add_argument("--test-days", type=int, default=28)
    parser.add_argument("--model", choices=("naive", "seasonal_naive", "moving_average_7", "hist_gradient_boosting"))
    args = parser.parse_args()
    results = run_project(horizon=args.horizon, test_days=args.test_days, forecast_model=args.model)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    for name in ("sales", "products"):
        path = args.raw_dir / f"demo_{name}.csv"
        results[name].to_csv(path, index=False)
        print(f"Wrote synthetic input {path}")
    for name in ("demand", "metrics", "forecast", "decisions"):
        path = args.output_dir / f"{name}.csv"
        results[name].to_csv(path, index=False)
        print(f"Wrote {path}")
    print("\nAggregate holdout metrics:")
    print(results["metrics"].query("sku_id == 'ALL'").to_string(index=False))
    print("\nInventory recommendations:")
    print(results["decisions"][["sku_id", "stockout_risk", "inventory_status", "recommended_order"]].to_string(index=False))


if __name__ == "__main__":
    main()
