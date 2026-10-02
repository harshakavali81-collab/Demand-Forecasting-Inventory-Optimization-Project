# Power BI blueprint

## Suggested star schema

Use `sql/schema.sql` as a starting point. Relate `dim_date` and `dim_product` one-to-many to the daily demand and inventory facts. Ensure each dimension key is unique and configure single-direction filtering unless a specific analysis needs otherwise.

## Report pages

1. **Executive overview:** units/revenue, stock risk counts, demand trend, category and inventory status.
2. **Demand forecast:** historical daily demand plus forecast table/line and SKU/category/date slicers.
3. **Inventory health:** on-hand, inbound, days of supply, reorder point, stockout-risk distribution.
4. **SKU analysis:** actual vs forecast, demand variability, ABC-XYZ segment, EOQ and order suggestion.
5. **Supplier view:** lead-time assumptions and SKU exposure; add actual fill rate/OTIF only with source data.

## Example DAX measures

```DAX
Units Sold = SUM ( fact_daily_demand[units_sold] )

Revenue = SUM ( fact_daily_demand[revenue] )

On Hand Units =
SUMX (
    VALUES ( fact_inventory_snapshot[sku_id] ),
    CALCULATE ( MAX ( fact_inventory_snapshot[on_hand_units] ) )
)

SKU Count = DISTINCTCOUNT ( dim_product[sku_id] )
```

The inventory measure assumes the report filter context selects the relevant snapshot date. Validate measures against SQL results. The demo does not claim to provide a Power BI `.pbix` binary; author the report in Power BI Desktop using governed data.
