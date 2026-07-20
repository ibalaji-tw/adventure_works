# Databricks notebook source
# Databricks Plotly page 2 — Customer Insights.

# COMMAND ----------

# MAGIC %run ./00_plotly_common

# COMMAND ----------

# STEP 1: Read customer Gold tables.
customers = gold_to_pandas(gold_customer_value_table)
segments = gold_to_pandas(gold_customer_segments_table)
monthly = gold_to_pandas(gold_sales_by_month_table)

# COMMAND ----------

# STEP 2: Reproduce the High Value, Repeat, and Standard findings.
segment_counts = customers["customer_segment"].value_counts()
show_plotly(metric_cards("Customer Findings", [
    ("Total Customers", len(customers), "", ""),
    ("High Value", int(segment_counts.get("High Value", 0)), "", ""),
    ("Repeat", int(segment_counts.get("Repeat", 0)), "", ""),
    ("Standard", int(segment_counts.get("Standard", 0)), "", ""),
]))

# COMMAND ----------

# STEP 3: Customer segment value — compare customer counts and revenue.
show_plotly(apply_style(px.bar(segments.sort_values("revenue"), x="revenue", y="customer_segment", orientation="h", color="customer_segment"), "Customer Segment Revenue"))
show_plotly(apply_style(px.bar(segments.sort_values("average_customer_value"), x="average_customer_value", y="customer_segment", orientation="h", color_discrete_sequence=["#F2C94C"]), "Average Customer Value by Segment"))

# COMMAND ----------

# STEP 4: Demographic visuals — reproduce the reference donut-style analysis.
gender = customers.assign(gender=customers["gender"].fillna("Unknown")).groupby("gender", as_index=False)["order_count"].sum()
show_plotly(apply_style(px.pie(gender, names="gender", values="order_count", hole=0.45), "Orders by Gender"))

income = customers.assign(income_band=pd.cut(customers["annual_income"], [-1, 50000, 100000, float("inf")], labels=["Low", "Average", "High"]))
income = income.groupby("income_band", observed=False, as_index=False)["order_count"].sum()
show_plotly(apply_style(px.pie(income, names="income_band", values="order_count", hole=0.45), "Orders by Income Band"))

occupation = customers.assign(occupation=customers["occupation"].fillna("Unknown")).groupby("occupation", as_index=False)["order_count"].sum()
show_plotly(apply_style(px.pie(occupation, names="occupation", values="order_count", hole=0.45), "Orders by Occupation"))

# COMMAND ----------

# STEP 5: Customer detail — show the highest-value customers.
display(customers.sort_values("lifetime_value", ascending=False).head(50))
