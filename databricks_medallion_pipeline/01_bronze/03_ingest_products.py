# Databricks notebook source
# Bronze 03 — Ingest product master data.

# COMMAND ----------

# STEP 0: Configuration — load shared source and destination names.
# MAGIC %run ../00_setup/00_setup

# STEP 1: Imports — load Spark types and functions.
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Schema — define the product source structure.
schema = StructType([
    StructField("ProductKey", IntegerType(), False), StructField("ProductSubcategoryKey", IntegerType(), True),
    StructField("ProductSKU", StringType(), True), StructField("ProductName", StringType(), True),
    StructField("ModelName", StringType(), True), StructField("ProductDescription", StringType(), True),
    StructField("ProductColor", StringType(), True), StructField("ProductSize", StringType(), True),
    StructField("ProductStyle", StringType(), True), StructField("ProductCost", DoubleType(), True),
    StructField("ProductPrice", DoubleType(), True),
])

# COMMAND ----------

# STEP 3: Configuration — define the source path and target table.
source_path = products_source_path
target_table = bronze_products_table

# COMMAND ----------

# STEP 4: Read — load the product file with no business transformations.
df = spark.read.format("csv").option("header", True).schema(schema).load(source_path)

# COMMAND ----------

# STEP 5: Metadata — add audit columns after the read.
df = df.withColumn("_source_file", F.input_file_name())
df = df.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------

# STEP 6: Validation — make sure the product key is present.
assert df.filter(F.col("ProductKey").isNull()).limit(1).count() == 0
display(df.limit(10))

# COMMAND ----------

# STEP 7: Database — create the target database if needed.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Write — reference data is safely full-refreshed in Bronze.
df.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(target_table)
