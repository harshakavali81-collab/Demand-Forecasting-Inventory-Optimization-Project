SET search_path TO inventory_analytics;

-- Monthly revenue and units.
SELECT date_trunc('month', d.date_key)::date AS month,
       SUM(f.units_sold) AS units,
       SUM(f.revenue) AS revenue
FROM fact_daily_demand AS f
JOIN dim_date AS d ON d.date_key = f.date_key
GROUP BY 1
ORDER BY 1;

-- Top SKUs and their share of total sales revenue.
WITH sku_revenue AS (
    SELECT p.sku_id, p.product_name, p.category, SUM(f.revenue) AS revenue
    FROM fact_daily_demand AS f
    JOIN dim_product AS p USING (sku_id)
    GROUP BY p.sku_id, p.product_name, p.category
)
SELECT *, revenue / NULLIF(SUM(revenue) OVER (), 0) AS revenue_share
FROM sku_revenue
ORDER BY revenue DESC
LIMIT 20;

-- Four-week moving average by SKU, using only current/prior dates.
SELECT sku_id, date_key, units_sold,
       AVG(units_sold) OVER (
           PARTITION BY sku_id ORDER BY date_key
           ROWS BETWEEN 27 PRECEDING AND CURRENT ROW
       ) AS rolling_28d_units
FROM fact_daily_demand;

-- Latest stock position by SKU.
WITH latest AS (
    SELECT DISTINCT ON (sku_id) sku_id, date_key, on_hand_units, inbound_units
    FROM fact_inventory_snapshot
    ORDER BY sku_id, date_key DESC
)
SELECT p.sku_id, p.product_name, latest.date_key,
       latest.on_hand_units, latest.inbound_units
FROM latest
JOIN dim_product AS p USING (sku_id)
ORDER BY latest.on_hand_units;
