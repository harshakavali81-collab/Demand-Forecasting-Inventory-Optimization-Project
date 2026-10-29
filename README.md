# Demand Forecasting & Inventory Optimization

An end-to-end, reproducible portfolio project that turns daily sales into demand forecasts and explainable replenishment recommendations. Includes synthetic demo data, validation and cleaning, time-aware model evaluation, inventory policies, Streamlit dashboard, FastAPI endpoint, PostgreSQL SQL, tests, and Docker setup.

[Setup](#local-installation--setup-guide) · [Architecture](#architecture--system-design-diagram) · [Detailed guide](PROJECT_GUIDE.md) · [Repository standard](docs/REPOSITORY_STANDARD.md)

## Visuals

![Project diagram / illustration](<reports/forecasting_workflow.svg>)

Existing project visual; diagrams and illustrative graphics are not evidence of a deployed application.

## Live Link / Demo

Run the local demo using the setup guide below. No public deployment URL has been verified for this documentation update.

## Key Features

The Streamlit dashboard provides demo-data or CSV-upload mode; configurable planning horizon, service level, days-of-supply target, and forecast model; category/SKU/risk filters; historical demand and forecast charts; model evaluation; inventory KPIs; and downloadable recommendation CSV. The FastAPI service exposes health and synthetic-demo decision endpoints.

## Tech Stack

![Python](https://img.shields.io/badge/Python-334155?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-334155?style=flat-square) ![Streamlit](https://img.shields.io/badge/Streamlit-334155?style=flat-square) ![scikit-learn](https://img.shields.io/badge/scikit--learn-334155?style=flat-square) ![Pandas](https://img.shields.io/badge/Pandas-334155?style=flat-square) ![NumPy](https://img.shields.io/badge/NumPy-334155?style=flat-square) ![SQL](https://img.shields.io/badge/SQL-334155?style=flat-square) ![Docker](https://img.shields.io/badge/Docker-334155?style=flat-square)

Dependency versions and optional packages are defined in the repository manifests.

## Architecture / System Design Diagram

[Architecture documentation / diagram](<reports/system_architecture.svg>)

## Local Installation & Setup Guide

```bash
git clone https://github.com/harshakavali81-collab/Demand-Forecasting-Inventory-Optimization-Project.git
cd Demand-Forecasting-Inventory-Optimization-Project
```

Python 3.10+ is recommended.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python -m demand_inventory.cli --output-dir data/processed --horizon 30
streamlit run dashboard/app.py
```

If `py` is unavailable, create the virtual environment using an installed Python executable. The CLI writes forecasts, evaluation scores, cleaned demand, and inventory decisions under `data/processed/`.

### Run with your own data

Provide two CSV files. The sales CSV must contain `order_id,order_date,sku_id,quantity,unit_price,discount,promotion`; the products CSV must contain `sku_id,product_name,category,unit_cost,current_stock,lead_time_days,minimum_order_quantity,order_cost,annual_holding_cost`. Dates should be parseable; returns may be negative quantities. Use the CLI:

```powershell
python -m demand_inventory.cli --sales-csv data/raw/sales.csv --products-csv data/raw/products.csv --horizon 30 --output-dir data/processed
```

Or select **Upload CSV files** in the Streamlit sidebar and upload both tables. Validate the business meaning of on-hand stock, order costs, returns, and lead times before relying on any output.

Run checks:

```powershell
python -m pytest
```

Run the JSON API in a separate terminal:

```powershell
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Challenges & Solutions

- Rows with invalid dates, unknown SKUs, non-finite numeric values, negative prices, or out-of-range discounts are excluded; duplicate order IDs are deduplicated. Returns are retained as negative transactions and netted against same-day sales; replenishment demand is floored at zero per SKU-day.
- Forecast tests use contiguous, chronological holdout dates, not random splitting. Future tree-model lag features are generated recursively from prior observations/predictions.
- WAPE is `sum(abs(actual - forecast)) / sum(abs(actual))`; it is undefined when total actual demand is zero and represented as blank/None.
- Safety stock uses the documented independent daily-demand/fixed-lead-time approximation: `z × daily-demand standard deviation × sqrt(lead time)`. Real operations should model lead-time demand directly, particularly with variable lead time.
- Reorder point is `mean daily demand × lead time + safety stock`.
- EOQ is `sqrt(2 × annual demand × order cost / annual holding cost per unit)`. MOQ and pack-size constraints should be added from actual supplier contracts.
- ABC class is based on cumulative revenue proxy; XYZ class uses demand coefficient of variation. Thresholds and caveats are in `docs/methodology.md`.
- Recommendations are decision support, not purchase orders. Review open orders, expiry, capacity, contract terms, data quality, and local processes.

## Future Improvements

This is a reference portfolio, not a production control system. It has no live ERP ingestion, authenticated access, purchase-order execution, promotion-plan feed, calibrated prediction intervals, or alerting. A production rollout requires data contracts, SKU-level backtesting, monitoring, approval controls, access management, and operational sign-off.

## Scope and supporting evidence

An end-to-end, reproducible portfolio project that turns daily sales into demand forecasts and explainable replenishment recommendations. Includes synthetic demo data, validation and cleaning, time-aware model evaluation, inventory policies, Streamlit dashboard, FastAPI endpoint, PostgreSQL SQL, tests, and Docker setup.

> **Demo data:** The built-in generator produces synthetic retail activity and illustrative supplier/stock assumptions. Model scores, products, financial measures, and recommendations are not observed business results or guaranteed savings. Replace demo inputs with licensed, validated business data before acting on recommendations.

## Repository Structure

| Location | Purpose |
| --- | --- |
| `src/` | Source modules |
| `tests/` | Tests |
| `docs/` | Documentation |
| `data/` | Data and samples |
| `sql/` | SQL schema and analysis |
| `scripts/` | Automation scripts |
| `.github/` | Issue forms, PR template and automated checks |

[Complete file inventory and workflow](docs/REPOSITORY_STANDARD.md). Runtime entry points retain their existing paths.

## Workflow & Tracking

Use the [bug and feature forms](https://github.com/harshakavali81-collab/Demand-Forecasting-Inventory-Optimization-Project/issues/new/choose) to define work with acceptance criteria. Keep tasks in Todo → In progress → Review → Done, and link a pull request with `Closes #<number>`. See [the maintenance workflow](docs/REPOSITORY_STANDARD.md#workflow).

## License

See [LICENSE](LICENSE) for the existing terms.
