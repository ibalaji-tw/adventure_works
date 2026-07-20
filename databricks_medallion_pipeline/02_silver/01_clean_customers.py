# Databricks notebook source
# Silver 01 — Clean customers and protect email addresses.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load Spark functions used for cleaning.
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Read — load the Bronze customer table.
source = spark.table(bronze_customers_table)

# COMMAND ----------

# STEP 3: Transform — cast fields, create a name, and mask email.
customers = (source
    .withColumn("customer_id", F.col("CustomerKey").cast("int"))
    .withColumn("birth_date", F.to_date("BirthDate", "M/d/yyyy"))
    .withColumn("annual_income", F.regexp_replace("AnnualIncome", r"[^0-9.-]", "").cast("double"))
    .withColumn("full_name", F.initcap(F.concat_ws(" ", "Prefix", "FirstName", "LastName")))
    .withColumn("email_address", F.concat(F.lit("***@"), F.regexp_extract("EmailAddress", r"@(.+)$", 1)))
    .select(
        "customer_id", "full_name", F.col("Prefix").alias("prefix"),
        F.col("FirstName").alias("first_name"), F.col("LastName").alias("last_name"),
        "birth_date", F.col("MaritalStatus").alias("marital_status"),
        F.col("Gender").alias("gender"), "email_address", "annual_income",
        F.col("TotalChildren").alias("total_children"),
        F.col("EducationLevel").alias("education_level"),
        F.col("Occupation").alias("occupation"), F.col("HomeOwner").alias("home_owner"),
    )
    .dropDuplicates(["customer_id"]))

# COMMAND ----------

# STEP 4: Validate — Silver customers must have unique, non-null keys.
assert customers.filter(F.col("customer_id").isNull()).limit(1).count() == 0
assert customers.filter(F.col("email_address").contains("@") == False).limit(1).count() == 0
display(customers.limit(10))

# COMMAND ----------

# STEP 5: Write — publish the cleaned customer dimension to Silver.
customers.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_customers_table)
