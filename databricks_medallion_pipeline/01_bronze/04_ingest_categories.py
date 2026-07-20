# Databricks notebook source
# Bronze 04 — Ingest product categories.

# COMMAND ----------

# STEP 0: Configuration — load shared source and destination names.
# MAGIC %run ../00_setup/00_setup

# STEP 1: Imports — load Spark types and functions.
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Schema — define the category source structure.
schema = StructType([StructField("ProductCategoryKey", IntegerType(), False), StructField("CategoryName", StringType(), False)])

# COMMAND ----------
# STEP 3: Configuration — define source and target names.
source_path = categories_source_path
target_table = bronze_categories_table

# COMMAND ----------
# STEP 4: Read — load the category file without cleaning it.
df = spark.read.format("csv").option("header", True).schema(schema).load(source_path)

# COMMAND ----------
# STEP 5: Metadata — record the source and ingestion time.
df = df.withColumn("_source_file", F.input_file_name())
df = df.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------
# STEP 6: Validation — category keys must be unique.
assert df.dropDuplicates(["ProductCategoryKey"]).count() == df.count()
display(df)

# COMMAND ----------
# STEP 7: Database — create the database if needed.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Write — small reference data is full-refreshed.
df.write.format("delta").mode("overwrite").saveAsTable(target_table)
