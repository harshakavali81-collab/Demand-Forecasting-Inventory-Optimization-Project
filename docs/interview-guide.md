# Interview and publication guide

## Short project pitch

“I built a reproducible retail demand-planning demo that transforms SKU sales into time-aware forecasts and explainable replenishment recommendations. I compared simple baselines with a tree model on a chronological holdout, then calculated service-level safety stock, reorder points, EOQ, and risk indicators. The data is synthetic, so I present the workflow and limitations rather than claiming business savings.”

## Discussion prompts

1. **Why forecast?** It makes future demand uncertainty visible before replenishment decisions.
2. **Why time split?** Random splits train on future patterns and leak information into evaluation.
3. **Why baselines?** A complex model is only useful when it improves on simple, credible alternatives.
4. **Why WAPE?** It is a volume-weighted aggregate error measure; it fails when total actual volume is zero.
5. **Why not MAPE?** It is undefined at zero and unstable near zero.
6. **Why recursive forecasting?** Future lag values are unknown; predictions fill those lags, with error compounding risk.
7. **How is safety stock calculated?** A service-level Z multiplier times daily standard deviation times square root of fixed lead time; this is an approximation.
8. **What is reorder point?** Expected demand during lead time plus buffer stock.
9. **What is EOQ?** Cost-based order-size estimate balancing fixed order and holding costs, subject to real supplier constraints.
10. **What does ABC-XYZ add?** A rough value and variability segmentation to tailor review priority.
11. **What are the primary limitations?** Synthetic data, one holdout origin, simple lead-time assumptions, and absent inbound/open orders.
12. **What would production need?** Licensed ERP feeds, data quality contracts, rolling-origin validation, monitoring, approvals, access controls, auditability, and a pilot.

## Resume bullets (edit to match what you actually did)

- Built a Python forecasting and inventory decision-support pipeline with SKU-day demand, lagged features, chronological model evaluation, and replenishment calculations.
- Delivered interactive Streamlit and read-only FastAPI interfaces with downloadable SKU recommendations and explicit assumption disclosures.
- Added PostgreSQL schema/query examples and automated tests for data cleaning, metrics, forecasting, and inventory formulas.

Do not claim business impact or model accuracy from the synthetic demonstration. Replace draft claims with independently measured outcomes only after a real pilot.
