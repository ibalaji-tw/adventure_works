# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze 01 — Ingest Customers
# MAGIC
# MAGIC **Purpose:** Land the customer source file in Delta with a controlled schema.
# MAGIC
# MAGIC **Why this is Bronze:** We preserve the source field names and values. We do
# MAGIC not yet clean currency, rename columns, or mask email addresses. That keeps
# MAGIC the landing layer replayable and makes the Silver rules easy to audit.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Set the customer source and target from shared configuration.
data_path = customers_source_path
target_table = bronze_customers_table

# For a local Spark test, change `customers_source_path` in the shared config.

# COMMAND ----------

# STEP 2: Imports — load Spark types and functions.
from pyspark.sql.types import StructField, StructType, IntegerType, StringType
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 3: Schema — describe the source before reading it.
customer_schema = StructType([
    StructField("CustomerKey", IntegerType(), nullable=False),
    StructField("Prefix", StringType(), nullable=True),
    StructField("FirstName", StringType(), nullable=True),
    StructField("LastName", StringType(), nullable=True),
    StructField("BirthDate", StringType(), nullable=True),
    StructField("MaritalStatus", StringType(), nullable=True),
    StructField("Gender", StringType(), nullable=True),
    StructField("EmailAddress", StringType(), nullable=True),
    # Keep the source currency text in Bronze. Silver will cast it to a number.
    StructField("AnnualIncome", StringType(), nullable=True),
    StructField("TotalChildren", IntegerType(), nullable=True),
    StructField("EducationLevel", StringType(), nullable=True),
    StructField("Occupation", StringType(), nullable=True),
    StructField("HomeOwner", StringType(), nullable=True),
])

# COMMAND ----------

# COMMAND ----------

# STEP 4: Read — load the customer file without business transformations.
customers_bronze = (spark.read
    .format("csv")
    .option("header", "true")
    .option("sep", "|")
    .option("quote", '"')
    .option("escape", '"')
    .schema(customer_schema)
    .load(data_path))

# COMMAND ----------

# STEP 5: Metadata — record where and when the source was loaded.
customers_bronze = customers_bronze.withColumn("_source_file", F.input_file_name())
customers_bronze = customers_bronze.withColumn("_ingestion_timestamp", F.current_timestamp())

# COMMAND ----------

# STEP 6: Validation — catch a wrong path or malformed customer data early.
assert customers_bronze.columns[:13] == customer_schema.fieldNames()
assert customers_bronze.filter(F.col("CustomerKey").isNull()).limit(1).count() == 0
assert customers_bronze.limit(1).count() == 1, "Customer source file is empty"

print(f"Bronze customer rows: {customers_bronze.count()}")
display(customers_bronze.limit(10))

# COMMAND ----------

# COMMAND ----------

# STEP 7: Database — create the database if this is the first run.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {bronze_schema}")

# COMMAND ----------

# STEP 8: Write — full-refresh this reference snapshot into Bronze.
(customers_bronze.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(target_table))

print(f"Written: {target_table}")

# COMMAND ----------

# Final verification: the table exists and has the expected row count.
display(spark.table(target_table).select(
    "CustomerKey", "FirstName", "LastName", "AnnualIncome", "_ingestion_timestamp"
).limit(10))
