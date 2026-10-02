# Methodology and caveats

## Cleaning and demand

Duplicate order IDs are dropped after first occurrence. Invalid dates, missing keys, non-finite quantities/prices, negative prices, unknown SKUs, and discounts outside `[0, 1]` are excluded. Negative quantity rows are returns; signed quantities are aggregated per SKU/day, then net daily demand is floored at zero. This assumption needs adaptation for businesses where returns are attributed to original sale dates.

## Features

For each SKU, lag 1/7/14/28 and rolling means of 7/14/28 use observations strictly before the target. Calendar fields are known for the future. The model is recursively forecast: each prediction becomes history for the next date, so horizon error may compound.

## Model comparison

The test set is the last `test_days` observations per SKU. Baselines: last-value naive, same weekday seven days ago, seven-day moving average. ML model: scikit-learn histogram gradient boosting on engineered features. Aggregate scores pool held-out SKU-days. Do not compare numbers across datasets/horizons as if they were universal. WAPE is undefined if aggregate actual demand is zero.

## Inventory equations

For service level `p`, let `z = NormalDist inverse CDF(p)`. Safety stock approximates `z * sigma_daily * sqrt(L)`, where `L` is fixed supplier lead time. Reorder point is `mu_daily * L + safety_stock`. EOQ is `sqrt(2 * D * S / H)` where `D` is annualized mean demand, `S` ordering cost, and `H` annual holding cost per unit. MOQ is applied to positive suggested quantity. `days_of_supply = stock / mean daily demand`; zero-mean SKUs have infinite days of supply.

ABC uses cumulative demand-value proxy (units × unit cost): A through 80%, B through 95%, and C remainder. XYZ uses coefficient of variation: X ≤ 0.5, Y ≤ 1.0, Z > 1.0; thresholds are illustrative. Revenue proxy is not gross margin or business criticality.

## Known limitations

No confidence intervals, multiple backtest folds, dynamic covariates, censoring correction for stockouts, open-order receipts, variable lead-time distribution, supplier calendars, pack-size constraints, budget/capacity optimization, live data, or automatic purchase execution. Current-stock values are generated assumptions. Every recommendation must be verified by a human.
