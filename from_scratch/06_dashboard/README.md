# Adventure Works dashboard

`Adventure_Works_Executive_Dashboard.lvdash.json` is a Databricks Lakeview dashboard definition. It reads only from the curated Gold tables in `adventure_works.gold`.

## Dashboard contents

- Total revenue, orders, units sold, and gross profit KPI cards
- Monthly revenue trend
- Revenue by category and territory
- Return rate by category
- Top products by gross profit
- Customer segment value

## Import in Databricks

1. Run the setup, Bronze, Silver, Gold, and quality notebooks so the tables exist.
2. In Databricks SQL, open **Dashboards** and choose **Create dashboard > Import dashboard**.
3. Select `Adventure_Works_Executive_Dashboard.lvdash.json`.
4. Select a SQL warehouse with permission to query the `adventure_works` catalog.
5. Review the widgets and publish the dashboard.

The dashboard file contains the serialized dashboard definition, including its SQL datasets and widget layout. The SQL warehouse is selected during import because it is workspace-specific and should not be hardcoded in source control.

## API note

For CI/CD, send the file contents as the `serialized_dashboard` value to the Databricks Lakeview dashboard create or update API and provide the target `warehouse_id` separately.
