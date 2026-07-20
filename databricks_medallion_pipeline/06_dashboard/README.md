# Adventure Works dashboard

`Adventure_Works_Executive_Dashboard.lvdash.json` is a Databricks Lakeview dashboard definition. It reads only from the curated Gold tables in `adventure_works.gold`.

## Dashboard pages and metrics

- **Executive Summary:** total revenue, orders, units sold, gross profit, monthly trend,
  category revenue, territory revenue, and return rate.
- **Customer Insights:** total customers plus High Value, Repeat, and Standard customer
  counts, segment value charts, and top-customer detail.
- **Product Details:** total products, product revenue, product gross profit, average
  margin, category contribution, top-product profit, and product detail.

The customer segments are defined in the Gold customer-value notebook: High Value
customers are at or above the 75th-percentile lifetime value, Repeat customers have
at least two orders, and the remaining customers are Standard.

For a Databricks-native Python/Plotly version, run the notebooks in
`databricks_plotly/`. They read the Gold Delta tables through Spark and render
the same three report pages directly in Databricks notebook output cells.

## Import in Databricks

1. Run the setup, Bronze, Silver, Gold, and quality notebooks so the tables exist.
2. In Databricks SQL, open **Dashboards** and choose **Create dashboard > Import dashboard**.
3. Select `Adventure_Works_Executive_Dashboard.lvdash.json`.
4. Select a SQL warehouse with permission to query the `adventure_works` catalog.
5. Review the widgets and publish the dashboard.

The dashboard file contains the serialized dashboard definition, including its SQL datasets and widget layout. The SQL warehouse is selected during import because it is workspace-specific and should not be hardcoded in source control.

## API note

For CI/CD, send the file contents as the `serialized_dashboard` value to the Databricks Lakeview dashboard create or update API and provide the target `warehouse_id` separately.
