# Databricks notebook source
# Gold 01 — Sales trend and commercial KPI table.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load aggregation functions.
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Read — load the Silver sales fact and product dimension.
sales = spark.table(silver_sales_table)
products = spark.table(silver_product_dimension_table)

# COMMAND ----------

# STEP 3: Calculate line values — derive revenue, cost, and gross profit.
sales_value = (sales.join(products.select("product_id", "product_price", "product_cost"), "product_id", "left")
    .withColumn("revenue", F.col("order_quantity") * F.col("product_price"))
    .withColumn("cost", F.col("order_quantity") * F.col("product_cost"))
    .withColumn("gross_profit", F.col("revenue") - F.col("cost")))

# COMMAND ----------

# STEP 4: Aggregate — create one row per calendar month.
sales_by_month = (sales_value.groupBy("order_year", "order_month", "order_month_start")
    .agg(F.round(F.sum("revenue"), 2).alias("revenue"),
         F.round(F.sum("cost"), 2).alias("cost"),
         F.round(F.sum("gross_profit"), 2).alias("gross_profit"),
         F.sum("order_quantity").alias("units_sold"),
         F.countDistinct("order_number").alias("order_count"),
         F.countDistinct("customer_id").alias("active_customers"))
    .withColumn("gross_margin_pct", F.round(F.col("gross_profit") / F.col("revenue") * 100, 2))
    .withColumn("average_order_value", F.round(F.col("revenue") / F.col("order_count"), 2)))

# COMMAND ----------

# STEP 5: Validate — Gold revenue must not be negative.
assert sales_by_month.filter(F.col("revenue") < 0).limit(1).count() == 0
display(sales_by_month.orderBy("order_month_start"))

# COMMAND ----------

# STEP 6: Write — publish the monthly sales Gold table.
sales_by_month.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(gold_sales_by_month_table)
