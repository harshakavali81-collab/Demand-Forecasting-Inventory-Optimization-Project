"""Command-line entry point for the end-to-end demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from demand_inventory.data import load_products, load_sales
from demand_inventory.service import run_project


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demand forecasting and inventory recommendations.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--sales-csv", type=Path, help="Transaction CSV with the documented sales columns.")
    parser.add_argument("--products-csv", type=Path, help="Product and replenishment assumption CSV.")
    parser.add_argument("--horizon", type=int, default=30)
    parser.add_argument("--test-days", type=int, default=28)
    parser.add_argument("--model", choices=("naive", "seasonal_naive", "moving_average_7", "hist_gradient_boosting"))
    args = parser.parse_args()
    if bool(args.sales_csv) != bool(args.products_csv):
        parser.error("--sales-csv and --products-csv must be supplied together.")
    if args.sales_csv and not args.sales_csv.is_file():
        parser.error(f"Sales CSV does not exist: {args.sales_csv}")
    if args.products_csv and not args.products_csv.is_file():
        parser.error(f"Products CSV does not exist: {args.products_csv}")
    sales = load_sales(args.sales_csv) if args.sales_csv else None
    products = load_products(args.products_csv) if args.products_csv else None
    results = run_project(
        horizon=args.horizon, test_days=args.test_days, forecast_model=args.model,
        sales=sales, products=products,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    if not args.sales_csv:
        for name in ("sales", "products"):
            path = args.raw_dir / f"demo_{name}.csv"
            results[name].to_csv(path, index=False)
            print(f"Wrote synthetic input {path}")
    for name in (
        "demand", "sku_summary", "category_summary", "metrics",
        "backtest_predictions", "forecast", "decisions",
    ):
        path = args.output_dir / f"{name}.csv"
        results[name].to_csv(path, index=False)
        print(f"Wrote {path}")
    print("\nAggregate holdout metrics:")
    print(results["metrics"].query("sku_id == 'ALL'").to_string(index=False))
    print("\nInventory recommendations:")
    print(results["decisions"][["sku_id", "stockout_risk", "inventory_status", "recommended_order"]].to_string(index=False))


if __name__ == "__main__":
    main()
