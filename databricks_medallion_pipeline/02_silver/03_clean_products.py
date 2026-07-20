# Databricks notebook source
# Silver 03 — Clean product and product hierarchy tables.

# COMMAND ----------

# STEP 0: Configuration — load shared source and destination names.
# MAGIC %run ../00_setup/00_setup

# STEP 1: Imports — load Spark functions for selection and casting.
from pyspark.sql import functions as F

# COMMAND ----------

# STEP 2: Read — load the three Bronze product hierarchy tables.
products_raw = spark.table(bronze_products_table)
categories_raw = spark.table(bronze_categories_table)
subcategories_raw = spark.table(bronze_subcategories_table)

# COMMAND ----------

# STEP 3: Transform products — standardize product names, types, and prices.
products = products_raw.select(
    F.col("ProductKey").cast("int").alias("product_id"),
    F.col("ProductSubcategoryKey").cast("int").alias("product_subcategory_id"),
    F.col("ProductSKU").alias("product_sku"), F.col("ProductName").alias("product_name"),
    F.col("ModelName").alias("model_name"), F.col("ProductDescription").alias("product_description"),
    F.col("ProductColor").alias("product_color"), F.col("ProductSize").alias("product_size"),
    F.round(F.col("ProductCost").cast("double"), 2).alias("product_cost"),
    F.round(F.col("ProductPrice").cast("double"), 2).alias("product_price"))

# COMMAND ----------

# STEP 4: Transform hierarchy — standardize category and subcategory keys.
categories = categories_raw.select(
    F.col("ProductCategoryKey").cast("int").alias("product_category_id"),
    F.col("CategoryName").alias("category_name"))
subcategories = subcategories_raw.select(
    F.col("ProductSubcategoryKey").cast("int").alias("product_subcategory_id"),
    F.col("SubcategoryName").alias("subcategory_name"),
    F.col("ProductCategoryKey").cast("int").alias("product_category_id"))

# COMMAND ----------

# STEP 5: Validate — product IDs must be unique and prices cannot be negative.
assert products.dropDuplicates(["product_id"]).count() == products.count()
assert products.filter(F.col("product_price") < 0).limit(1).count() == 0
display(products.limit(10))

# COMMAND ----------

# STEP 6: Write dimensions — publish the three cleaned Silver dimensions.
products.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_products_table)
categories.write.format("delta").mode("overwrite").saveAsTable(silver_categories_table)
subcategories.write.format("delta").mode("overwrite").saveAsTable(silver_subcategories_table)

# COMMAND ----------

# STEP 7: Enrich — join products to subcategory and category.
product_dimension = (products.join(subcategories, "product_subcategory_id", "left")
    .join(categories, "product_category_id", "left"))

# COMMAND ----------

# STEP 8: Write conformed dimension — publish one reusable product hierarchy.
product_dimension.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_product_dimension_table)
display(product_dimension.limit(10))
