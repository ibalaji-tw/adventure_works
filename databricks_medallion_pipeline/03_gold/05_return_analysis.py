# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Gold 05 — Product and category return analysis.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load aggregation functions.
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Read — load Silver sales, product dimension, and returns.
sales = spark.table(silver_sales_table)
products = spark.table(silver_product_dimension_table)
returns = spark.table(silver_returns_table)

# COMMAND ----------

# STEP 3: Aggregate sold units — calculate sales volume by product.
sold = sales.groupBy("product_id").agg(F.sum("order_quantity").alias("sold_units"))

# COMMAND ----------

# STEP 4: Aggregate returned units — calculate returns by product.
returned = returns.groupBy("product_id").agg(F.sum("return_quantity").alias("returned_units"))

# COMMAND ----------

# STEP 5: Calculate product return rate — join sales, returns, and product names.
return_by_product = (sold.join(returned, "product_id", "left").fillna(0, ["returned_units"])
    .join(products.select("product_id", "product_name", "category_name", "subcategory_name"), "product_id", "left")
    .withColumn("return_rate_pct", F.round(F.col("returned_units") / F.col("sold_units") * 100, 2)))

# COMMAND ----------

# STEP 6: Validate and inspect — return rate should be between 0 and 100 percent.
assert return_by_product.filter(F.col("return_rate_pct") > 100).limit(1).count() == 0
display(return_by_product.orderBy(F.desc("return_rate_pct")).limit(20))

# COMMAND ----------

# STEP 7: Write products — publish product-level return analysis.
return_by_product.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(gold_return_by_product_table)

# COMMAND ----------

# STEP 8: Aggregate categories — summarize sold units and returns by hierarchy.
return_by_category = (return_by_product.groupBy("category_name", "subcategory_name")
    .agg(F.sum("sold_units").alias("sold_units"), F.sum("returned_units").alias("returned_units"))
    .withColumn("return_rate_pct", F.round(F.col("returned_units") / F.col("sold_units") * 100, 2)))
display(return_by_category)

# COMMAND ----------

# STEP 9: Write categories — publish category-level return analysis.
return_by_category.write.format("delta").mode("overwrite").saveAsTable(gold_return_by_category_table)
