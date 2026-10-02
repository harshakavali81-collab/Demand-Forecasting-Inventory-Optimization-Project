"""Input loading and deterministic synthetic retail data for the demo."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SALES_COLUMNS = [
    "order_id", "order_date", "sku_id", "quantity", "unit_price",
    "discount", "promotion",
]
PRODUCT_COLUMNS = [
    "sku_id", "product_name", "category", "unit_cost", "current_stock",
    "lead_time_days", "minimum_order_quantity", "order_cost",
    "annual_holding_cost",
]


def generate_demo_data(
    start_date: str = "2024-01-01",
    periods: int = 540,
    seed: int = 17,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate repeatable synthetic daily sales and SKU/supplier assumptions."""
    if periods < 35:
        raise ValueError("periods must be at least 35 days.")
    rng = np.random.default_rng(seed)
    products = pd.DataFrame(
        [
            ("SKU-001", "Everyday Backpack", "Accessories", 18.0, 310, 8, 12, 45.0, 4.5),
            ("SKU-002", "Insulated Bottle", "Home", 8.0, 155, 5, 24, 35.0, 2.2),
            ("SKU-003", "Wireless Mouse", "Electronics", 14.0, 92, 12, 10, 55.0, 3.8),
            ("SKU-004", "Desk Lamp", "Home", 21.0, 240, 9, 8, 48.0, 4.0),
            ("SKU-005", "Running Socks", "Apparel", 4.0, 520, 6, 50, 28.0, 1.3),
            ("SKU-006", "Travel Adapter", "Electronics", 11.0, 68, 14, 10, 60.0, 3.2),
            ("SKU-007", "Yoga Mat", "Fitness", 16.0, 205, 7, 12, 42.0, 3.1),
            ("SKU-008", "Ceramic Mug", "Home", 6.0, 410, 4, 24, 30.0, 1.7),
        ],
        columns=PRODUCT_COLUMNS,
    )
    dates = pd.date_range(start_date, periods=periods, freq="D")
    records: list[dict[str, object]] = []
    base_rates = np.array([13, 18, 9, 7, 26, 6, 11, 19], dtype=float)
    for sku_index, product in products.iterrows():
        weekday = dates.dayofweek.to_numpy()
        seasonal = 1.0 + 0.18 * np.sin(2 * np.pi * dates.dayofyear.to_numpy() / 365.25)
        weekend = np.where(weekday >= 5, 1.18, 0.92)
        promotion = rng.binomial(1, 0.055, size=periods)
        rate = base_rates[sku_index] * seasonal * weekend * (1 + 0.3 * promotion)
        quantities = rng.poisson(rate).astype(int)
        for day_index, date in enumerate(dates):
            records.append(
                {
                    "order_id": f"{product.sku_id}-{date:%Y%m%d}",
                    "order_date": date,
                    "sku_id": product.sku_id,
                    "quantity": int(quantities[day_index]),
                    "unit_price": round(float(product.unit_cost) * 2.2, 2),
                    "discount": 0.10 if promotion[day_index] else 0.0,
                    "promotion": bool(promotion[day_index]),
                }
            )
    return pd.DataFrame.from_records(records, columns=SALES_COLUMNS), products


def load_sales(path: str | Path) -> pd.DataFrame:
    """Load transaction-level sales from CSV."""
    return pd.read_csv(path, parse_dates=["order_date"])


def load_products(path: str | Path) -> pd.DataFrame:
    """Load product and replenishment assumptions from CSV."""
    return pd.read_csv(path)
