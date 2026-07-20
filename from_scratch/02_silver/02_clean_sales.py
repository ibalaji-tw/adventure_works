# Databricks notebook source
# Silver 02 — Standardize and deduplicate sales lines.

# COMMAND ----------

# STEP 0: Configuration — load shared source and destination names.
# MAGIC %run ../00_setup/00_setup

# STEP 1: Imports — load functions and the window API for deduplication.
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# STEP 2: Read — load Bronze sales and define the business line key.
source = spark.table(bronze_sales_table)
latest_line = Window.partitionBy("OrderNumber", "OrderLineItem").orderBy(F.col("_ingestion_timestamp").desc())

# COMMAND ----------

# STEP 3: Transform — cast dates/keys and create calendar fields.
sales = (source
    .withColumn("order_date", F.to_date("OrderDate", "M/d/yyyy"))
    .withColumn("stock_date", F.to_date("StockDate", "M/d/yyyy"))
    .withColumn("order_number", F.col("OrderNumber"))
    .withColumn("product_id", F.col("ProductKey").cast("int"))
    .withColumn("customer_id", F.col("CustomerKey").cast("int"))
    .withColumn("territory_id", F.col("TerritoryKey").cast("int"))
    .withColumn("order_line_item", F.col("OrderLineItem").cast("int"))
    .withColumn("order_quantity", F.col("OrderQuantity").cast("int"))
    .withColumn("row_number", F.row_number().over(latest_line))
    .filter((F.col("row_number") == 1) & F.col("order_date").isNotNull() & (F.col("order_quantity") > 0))
    .withColumn("order_year", F.year("order_date"))
    .withColumn("order_month", F.month("order_date"))
    .withColumn("order_month_start", F.trunc("order_date", "month"))
    .select("order_number", "order_line_item", "order_date", "stock_date", "order_year",
            "order_month", "order_month_start", "product_id", "customer_id", "territory_id", "order_quantity"))

# COMMAND ----------

# STEP 4: Validate — confirm one row per order line and valid quantities.
assert sales.filter(F.col("order_number").isNull()).limit(1).count() == 0
assert sales.filter(F.col("order_quantity") <= 0).limit(1).count() == 0
assert sales.groupBy("order_number", "order_line_item").count().filter("count > 1").limit(1).count() == 0
display(sales.limit(10))

# COMMAND ----------

# STEP 5: Write — publish the clean sales fact to Silver.
sales.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_sales_table)
