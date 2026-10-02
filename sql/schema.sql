-- PostgreSQL starter star schema. Load dimensions before facts.
CREATE SCHEMA IF NOT EXISTS inventory_analytics;
SET search_path TO inventory_analytics;

CREATE TABLE IF NOT EXISTS dim_product (
    sku_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key DATE PRIMARY KEY,
    year SMALLINT NOT NULL,
    month SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_daily_demand (
    sku_id TEXT NOT NULL REFERENCES dim_product(sku_id),
    date_key DATE NOT NULL REFERENCES dim_date(date_key),
    units_sold NUMERIC(14, 2) NOT NULL CHECK (units_sold >= 0),
    revenue NUMERIC(14, 2) NOT NULL CHECK (revenue >= 0),
    PRIMARY KEY (sku_id, date_key)
);

CREATE TABLE IF NOT EXISTS fact_inventory_snapshot (
    sku_id TEXT NOT NULL REFERENCES dim_product(sku_id),
    date_key DATE NOT NULL REFERENCES dim_date(date_key),
    on_hand_units NUMERIC(14, 2) NOT NULL CHECK (on_hand_units >= 0),
    inbound_units NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (inbound_units >= 0),
    PRIMARY KEY (sku_id, date_key)
);

CREATE INDEX IF NOT EXISTS ix_daily_demand_date ON fact_daily_demand(date_key);
CREATE INDEX IF NOT EXISTS ix_inventory_date ON fact_inventory_snapshot(date_key);
