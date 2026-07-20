# Databricks notebook source
# Gold 02 — Product, category, and subcategory profitability.

# COMMAND ----------

# STEP 0: Configuration — load shared source and destination names.
# MAGIC %run ../00_setup/00_setup

# STEP 1: Imports — load aggregation and ranking functions.
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# STEP 2: Read — load Silver sales and the conformed product dimension.
sales = spark.table(silver_sales_table)
products = spark.table(silver_product_dimension_table)

# COMMAND ----------

# STEP 3: Calculate line values — derive revenue, cost, and gross profit.
product_sales = (sales.join(products, "product_id", "left")
    .withColumn("revenue", F.col("order_quantity") * F.col("product_price"))
    .withColumn("cost", F.col("order_quantity") * F.col("product_cost"))
    .withColumn("gross_profit", F.col("revenue") - F.col("cost")))

# COMMAND ----------

# STEP 4: Aggregate and rank — calculate product profitability and rankings.
product_performance = (product_sales.groupBy("product_id", "product_name", "category_name", "subcategory_name")
    .agg(F.sum("order_quantity").alias("units_sold"), F.countDistinct("order_number").alias("order_count"),
         F.round(F.sum("revenue"), 2).alias("revenue"), F.round(F.sum("cost"), 2).alias("cost"),
         F.round(F.sum("gross_profit"), 2).alias("gross_profit"))
    .withColumn("gross_margin_pct", F.round(F.col("gross_profit") / F.col("revenue") * 100, 2))
    .withColumn("profit_rank", F.dense_rank().over(Window.orderBy(F.desc("gross_profit"))))
    .withColumn("revenue_rank", F.dense_rank().over(Window.orderBy(F.desc("revenue")))))

# COMMAND ----------

# STEP 5: Validate and inspect — every product must have a product key.
assert product_performance.filter(F.col("product_id").isNull()).limit(1).count() == 0
display(product_performance.orderBy("profit_rank").limit(20))

# COMMAND ----------

# STEP 6: Write products — publish the product-level Gold table.
product_performance.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(gold_product_performance_table)

# COMMAND ----------

# STEP 7: Aggregate categories — prepare a smaller dashboard table.
category_performance = (product_performance.groupBy("category_name")
    .agg(F.sum("units_sold").alias("units_sold"), F.sum("revenue").alias("revenue"),
         F.sum("gross_profit").alias("gross_profit"))
    .withColumn("gross_margin_pct", F.round(F.col("gross_profit") / F.col("revenue") * 100, 2)))
display(category_performance)

# COMMAND ----------

# STEP 8: Write categories — publish the category-level Gold table.
category_performance.write.format("delta").mode("overwrite").saveAsTable(gold_category_performance_table)
