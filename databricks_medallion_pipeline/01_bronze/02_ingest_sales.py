# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Bronze 02 — Ingest the three yearly sales files.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load Spark types and functions.
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Schema — define the schema shared by every yearly sales file.
sales_schema = StructType([
    StructField("OrderDate", StringType(), False), StructField("StockDate", StringType(), True),
    StructField("OrderNumber", StringType(), False), StructField("ProductKey", IntegerType(), False),
    StructField("CustomerKey", IntegerType(), False), StructField("TerritoryKey", IntegerType(), False),
    StructField("OrderLineItem", IntegerType(), False), StructField("OrderQuantity", IntegerType(), False),
])

# COMMAND ----------

# STEP 3: Configuration — Spark reads every file currently inside this folder.
sales_path = sales_source_path
target_table = bronze_sales_table

# COMMAND ----------

# STEP 4: Read — load all yearly files from the folder.
sales_bronze = (spark.read.format("csv").option("header", True)
    .schema(sales_schema).load(sales_path))

# COMMAND ----------

# STEP 5: Metadata — add source file and ingestion timestamp separately.
sales_bronze = sales_bronze.withColumn("_source_file", F.input_file_name())
sales_bronze = sales_bronze.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------

# STEP 6: Validation — confirm the folder contains data and required keys.
assert sales_bronze.limit(1).count() == 1, "Sales source is empty"
assert sales_bronze.filter(F.col("OrderNumber").isNull()).limit(1).count() == 0
print(f"Bronze sales rows: {sales_bronze.count()}")
display(sales_bronze.limit(10))

# COMMAND ----------

# STEP 7: Database — create the database if this is the first run.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Incremental write — keep only order lines not already in Bronze.
# Rerunning the notebook is therefore safe, and a new 2018 file is picked up.
if spark.catalog.tableExists(target_table):
    existing_keys = spark.table(target_table).select("OrderNumber", "OrderLineItem").dropDuplicates()
    new_sales = sales_bronze.join(existing_keys, ["OrderNumber", "OrderLineItem"], "left_anti")
else:
    new_sales = sales_bronze

new_count = new_sales.count()
print(f"New sales rows to append: {new_count}")
if new_count > 0:
    new_sales.write.format("delta").mode("append").saveAsTable(target_table)
print(f"Written incrementally: {target_table}")
