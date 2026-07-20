# Databricks notebook source
# Databricks Plotly page 1 — Executive Summary.

# COMMAND ----------

# MAGIC %run ./00_plotly_common

# COMMAND ----------

# STEP 1: Read the Gold-layer datasets used by the executive report.
monthly = gold_to_pandas(gold_sales_by_month_table)
category = gold_to_pandas(gold_category_performance_table)
subcategory = gold_to_pandas(gold_product_performance_table)
products = gold_to_pandas(gold_product_performance_table)
returns = gold_to_pandas(gold_return_by_product_table)

# COMMAND ----------

# STEP 2: KPI cards — summarize commercial performance.
show_plotly(metric_cards("Executive Summary", [
    ("Total Revenue", monthly["revenue"].sum(), "$", ""),
    ("Total Orders", monthly["order_count"].sum(), "", ""),
    ("Units Sold", monthly["units_sold"].sum(), "", ""),
    ("Gross Profit", monthly["gross_profit"].sum(), "$", ""),
]))

# COMMAND ----------

# STEP 3: Monthly revenue trend — reproduce the reference trend visual.
monthly["order_month_start"] = pd.to_datetime(monthly["order_month_start"])
show_plotly(apply_style(px.area(monthly.sort_values("order_month_start"), x="order_month_start", y="revenue", color_discrete_sequence=["#00AFA5"]), "Monthly Revenue"))

# COMMAND ----------

# STEP 4: Category and subcategory order breakdowns.
show_plotly(apply_style(px.bar(category.sort_values("units_sold"), x="units_sold", y="category_name", orientation="h", color="category_name"), "Total Orders by Category"))
subcategory_summary = (subcategory.groupby("subcategory_name", as_index=False)["units_sold"].sum().sort_values("units_sold", ascending=False).head(15))
show_plotly(apply_style(px.bar(subcategory_summary.sort_values("units_sold"), x="units_sold", y="subcategory_name", orientation="h", color_discrete_sequence=["#00AFA5"]), "Total Orders by Subcategory"))

# COMMAND ----------

# STEP 5: Product and return findings — show top products and return hotspots.
show_plotly(apply_style(px.bar(products.sort_values("gross_profit", ascending=False).head(15).sort_values("gross_profit"), x="gross_profit", y="product_name", orientation="h", color_discrete_sequence=["#00AFA5"]), "Top Products by Gross Profit"))
show_plotly(apply_style(px.bar(returns.sort_values("return_rate_pct", ascending=False).head(15).sort_values("return_rate_pct"), x="return_rate_pct", y="product_name", orientation="h", color_discrete_sequence=["#FF6B6B"]), "Product Return Rate Hotspots"))

# COMMAND ----------

# STEP 6: Detail table — use Databricks native table rendering for exploration.
display(products.sort_values("gross_profit", ascending=False).limit(20) if hasattr(products, "limit") else products.sort_values("gross_profit", ascending=False).head(20))
