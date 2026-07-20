# Databricks notebook source
# Bronze 07 — Ingest the multi-line JSON returns file.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load Spark types and functions.
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Schema — define the multi-line JSON return structure.
schema = StructType([
    StructField("ReturnDate", StringType(), False), StructField("TerritoryKey", IntegerType(), False),
    StructField("ProductKey", IntegerType(), False), StructField("ReturnQuantity", IntegerType(), False),
])

# COMMAND ----------
# STEP 3: Configuration — define source and target names.
source_path = returns_source_path
target_table = bronze_returns_table

# COMMAND ----------
# STEP 4: Read — multiLine is required because the JSON is an array.
df = spark.read.format("json").option("multiLine", True).schema(schema).load(source_path)

# COMMAND ----------
# STEP 5: Metadata — add audit columns separately.
df = df.withColumn("_source_file", F.input_file_name())
df = df.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------
# STEP 6: Validation — keys and quantities must be valid.
assert df.filter(F.col("ProductKey").isNull()).limit(1).count() == 0
assert df.filter(F.col("ReturnQuantity") <= 0).limit(1).count() == 0
display(df.limit(10))

# COMMAND ----------
# STEP 7: Database — create the database if needed.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Write — return data is full-refreshed for this static snapshot.
df.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(target_table)
