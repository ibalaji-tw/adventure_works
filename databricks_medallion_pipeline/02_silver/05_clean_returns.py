# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Silver 05 — Parse and standardize return events.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load functions for dates and type casting.
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Read — load the Bronze returns table.
source = spark.table(bronze_returns_table)

# COMMAND ----------

# STEP 3: Transform — parse dates and create return calendar fields.
return_date = F.to_date("ReturnDate", "M/d/yyyy")
returns = (source
    .select(return_date.alias("return_date"), F.year(return_date).alias("return_year"),
            F.month(return_date).alias("return_month"),
            F.col("TerritoryKey").cast("int").alias("territory_id"),
            F.col("ProductKey").cast("int").alias("product_id"),
            F.col("ReturnQuantity").cast("int").alias("return_quantity"))
    .filter(F.col("return_date").isNotNull() & (F.col("return_quantity") > 0)))

# COMMAND ----------

# STEP 4: Validate — return product keys and quantities must be valid.
assert returns.filter(F.col("product_id").isNull()).limit(1).count() == 0
assert returns.filter(F.col("return_quantity") <= 0).limit(1).count() == 0
display(returns.limit(10))

# COMMAND ----------

# STEP 5: Write — publish the clean returns fact to Silver.
returns.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_returns_table)
