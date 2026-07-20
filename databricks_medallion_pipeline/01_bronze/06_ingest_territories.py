# Databricks notebook source
# Bronze 06 — Ingest sales territories.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load Spark types and functions.
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Schema — define the tab-delimited territory structure.
schema = StructType([
    StructField("SalesTerritoryKey", IntegerType(), False), StructField("Region", StringType(), True),
    StructField("Country", StringType(), True), StructField("Continent", StringType(), True),
    StructField("manager", StringType(), True),
])

# COMMAND ----------
# STEP 3: Configuration — define source and target names.
source_path = territories_source_path
target_table = bronze_territories_table

# COMMAND ----------
# STEP 4: Read — use tab as the source delimiter.
df = spark.read.format("csv").option("header", True).option("sep", "\t").schema(schema).load(source_path)

# COMMAND ----------
# STEP 5: Metadata — add audit columns separately.
df = df.withColumn("_source_file", F.input_file_name())
df = df.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------
# STEP 6: Validation — territory keys must be unique.
assert df.dropDuplicates(["SalesTerritoryKey"]).count() == df.count()
display(df)

# COMMAND ----------
# STEP 7: Database — create the database if needed.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Write — reference data is full-refreshed.
df.write.format("delta").mode("overwrite").saveAsTable(target_table)
