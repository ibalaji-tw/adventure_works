# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Bronze 05 — Ingest product subcategories.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load Spark types and functions.
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Schema — define the subcategory source structure.
schema = StructType([
    StructField("ProductSubcategoryKey", IntegerType(), False),
    StructField("SubcategoryName", StringType(), False),
    StructField("ProductCategoryKey", IntegerType(), False),
])

# COMMAND ----------
# STEP 3: Configuration — define source and target names.
source_path = subcategories_source_path
target_table = bronze_subcategories_table

# COMMAND ----------
# STEP 4: Read — load the source subcategories.
df = spark.read.format("csv").option("header", True).schema(schema).load(source_path)

# COMMAND ----------
# STEP 5: Metadata — add audit columns separately.
df = df.withColumn("_source_file", F.input_file_name())
df = df.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------
# STEP 6: Validation — every subcategory must have a category key.
assert df.filter(F.col("ProductCategoryKey").isNull()).limit(1).count() == 0
display(df)

# COMMAND ----------
# STEP 7: Database — create the database if needed.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Write — reference data is full-refreshed.
df.write.format("delta").mode("overwrite").saveAsTable(target_table)
