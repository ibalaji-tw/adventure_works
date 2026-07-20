# Databricks-native Plotly dashboard notebooks

These notebooks are designed to run directly in Databricks. They do not start
a web server and do not depend on Dash. Each notebook reads the Adventure Works
Gold Delta tables through Spark and renders Plotly figures in Databricks output
cells.

## Three report pages

1. `01_executive_summary.py` — executive KPIs, revenue trend, category and
   subcategory orders, product profitability, and return hotspots.
2. `02_customer_insights.py` — High Value, Repeat, and Standard customer KPIs,
   segment value, gender/income/occupation visuals, and customer detail.
3. `03_product_details.py` — product KPIs, category/product profitability,
   monthly gross profit, return rate, and product detail.

## Run order

1. Run `00_setup/00_setup.py`.
2. Run Bronze, Silver, Gold, and quality notebooks.
3. Run each Plotly page notebook.
4. Use the Databricks notebook output cells to build a notebook dashboard, or
   add the individual visualizations to a Databricks dashboard.
