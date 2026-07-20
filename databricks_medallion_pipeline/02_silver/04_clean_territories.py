# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Silver 04 — Standardize territories and protect the manager email.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load functions for casting and masking.
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Read — load the Bronze territory table.
source = spark.table(bronze_territories_table)

# COMMAND ----------

# STEP 3: Transform — standardize names and mask manager email.
territories = (source
    .select(F.col("SalesTerritoryKey").cast("int").alias("territory_id"),
            F.col("Region").alias("region"), F.col("Country").alias("country"),
            F.col("Continent").alias("continent"),
            F.concat(F.lit("***@"), F.regexp_extract("manager", r"@(.+)$", 1)).alias("manager_email"))
    .dropDuplicates(["territory_id"]))

# COMMAND ----------

# STEP 4: Validate — territories must have unique, non-null keys.
assert territories.filter(F.col("territory_id").isNull()).limit(1).count() == 0
display(territories)

# COMMAND ----------

# STEP 5: Write — publish the clean territory dimension.
territories.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_territories_table)
