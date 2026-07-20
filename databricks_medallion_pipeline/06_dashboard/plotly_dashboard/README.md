# Plotly dashboard

This is a companion Python Plotly Dash implementation of the three reference
reports. It uses the repository `data/` folder and provides the same pages:

- Executive Summary
- Customer Insights, including High Value, Repeat, and Standard segments
- Product Details

## Run locally

```bash
cd databricks_medallion_pipeline/06_dashboard/plotly_dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8050` in a browser.

The app computes its metrics from the included source files using the same
business rules as the Gold layer. In Databricks, the same layout can be adapted
to query the Gold Delta tables directly instead of reading CSV files.
