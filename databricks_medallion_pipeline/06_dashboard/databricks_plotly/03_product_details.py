# Databricks notebook source
# Databricks Plotly page 3 — Product Details.

# COMMAND ----------

# MAGIC %run ./00_plotly_common

# COMMAND ----------

# STEP 1: Read product and return Gold tables.
products = gold_to_pandas(gold_product_performance_table)
categories = gold_to_pandas(gold_category_performance_table)
returns = gold_to_pandas(gold_return_by_product_table)
monthly = gold_to_pandas(gold_sales_by_month_table)

# COMMAND ----------

# STEP 2: Product KPI cards — reproduce the reference product metrics.
show_plotly(metric_cards("Product Details", [
    ("Total Products", products["product_id"].nunique(), "", ""),
    ("Product Revenue", products["revenue"].sum(), "$", ""),
    ("Product Gross Profit", products["gross_profit"].sum(), "$", ""),
    ("Average Margin", products["gross_margin_pct"].mean(), "", "%"),
]))

# COMMAND ----------

# STEP 3: Category and product profitability visuals.
show_plotly(apply_style(px.bar(categories.sort_values("revenue"), x="revenue", y="category_name", orientation="h", color_discrete_sequence=["#00AFA5"]), "Category Revenue"))
top_products = products.sort_values("gross_profit", ascending=False).head(20).sort_values("gross_profit")
show_plotly(apply_style(px.bar(top_products, x="gross_profit", y="product_name", orientation="h", color_discrete_sequence=["#00AFA5"]), "Top Products by Gross Profit"))

# COMMAND ----------

# STEP 4: Monthly profit and product returns — reproduce the reference trend views.
monthly["order_month_start"] = pd.to_datetime(monthly["order_month_start"])
show_plotly(apply_style(px.line(monthly.sort_values("order_month_start"), x="order_month_start", y="gross_profit", color_discrete_sequence=["#00AFA5"]), "Monthly Gross Profit"))
show_plotly(apply_style(px.bar(returns.sort_values("return_rate_pct", ascending=False).head(15).sort_values("return_rate_pct"), x="return_rate_pct", y="product_name", orientation="h", color_discrete_sequence=["#FF6B6B"]), "Product Return Rate"))

# COMMAND ----------

# STEP 5: Product profitability detail table.
display(products.sort_values("gross_profit", ascending=False).head(100))
