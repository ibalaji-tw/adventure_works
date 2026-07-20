# Gold layer

Each `.py` file is a Databricks notebook. The `# COMMAND ----------` markers
separate the business logic into runnable cells, and each cell documents one
business step before the next step is executed.

Gold tables answer business questions from the Silver model. The important
definitions are visible in the notebooks:

- Revenue = `order_quantity * product_price`
- Cost = `order_quantity * product_cost`
- Gross profit = revenue - cost
- Return rate = returned units / sold units
- High Value customers = customers at or above the 75th percentile of lifetime value
- Repeat customers = customers with at least two orders who are below the High Value threshold

Tables produced:

```text
adventure_works.gold.sales_by_month
adventure_works.gold.product_performance
adventure_works.gold.category_performance
adventure_works.gold.customer_value
adventure_works.gold.customer_segments
adventure_works.gold.territory_performance
adventure_works.gold.return_by_product
adventure_works.gold.return_by_category
```
