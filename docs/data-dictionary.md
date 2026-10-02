# Data dictionary

The demo exposes a transaction table and a SKU assumptions table. Numeric demonstration values are synthetic. The CSV loader accepts these same schemas.

## Sales transactions

| Field | Type | Meaning |
|---|---|---|
| `order_id` | string | Unique transaction/day identifier |
| `order_date` | date | Transaction date |
| `sku_id` | string | Product identifier, foreign key |
| `quantity` | integer | Units; negative values represent returns |
| `unit_price` | decimal | Non-negative selling price assumption |
| `discount` | decimal | Fraction in `[0, 1]` |
| `promotion` | boolean | Demo promotion indicator |

## Product / replenishment assumptions

| Field | Type | Meaning |
|---|---|---|
| `sku_id` | string | Unique SKU |
| `product_name` | string | Fictional product label |
| `category` | string | Fictional merchandising category |
| `unit_cost` | decimal | Demo unit cost; also used in ABC proxy |
| `current_stock` | integer | Simulated on-hand starting quantity |
| `lead_time_days` | integer | Assumed replenishment lead time |
| `minimum_order_quantity` | integer | Assumed supplier MOQ |
| `order_cost` | decimal | Assumed fixed cost per purchase order |
| `annual_holding_cost` | decimal | Assumed annual holding cost per unit |

## Derived output

`demand.csv`: SKU-day floored net units; `forecast.csv`: SKU/date expected units; `metrics.csv`: model, MAE, RMSE, WAPE by SKU and pooled; `decisions.csv`: forecast total, demand statistics, safety stock, reorder point, EOQ, days of supply, suggested order, risk/status, ABC-XYZ segment.

The generated `reports/data_dictionary.xlsx` contains these definitions plus output fields and explicit provenance/assumption notes.
