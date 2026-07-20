# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Gold 04 — Territory sales and return performance.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

# STEP 1: Imports — load aggregation and ranking functions.
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# STEP 2: Read — load Silver sales, products, territories, and returns.
sales = spark.table(silver_sales_table)
products = spark.table(silver_product_dimension_table)
territories = spark.table(silver_territories_table)
returns = spark.table(silver_returns_table)

# COMMAND ----------

# STEP 3: Aggregate sales — calculate revenue, units, and orders by territory.
sales_by_territory = (sales.join(products.select("product_id", "product_price"), "product_id", "left")
    .groupBy("territory_id")
    .agg(F.sum(F.col("order_quantity") * F.col("product_price")).alias("revenue"),
         F.sum("order_quantity").alias("units_sold"), F.countDistinct("order_number").alias("order_count")))

# COMMAND ----------

# STEP 4: Aggregate returns — calculate returned units by territory.
returns_by_territory = returns.groupBy("territory_id").agg(F.sum("return_quantity").alias("returned_units"))

# COMMAND ----------

# STEP 5: Enrich and calculate — join territory names and return rate.
territory_performance = (sales_by_territory.join(returns_by_territory, "territory_id", "left").fillna(0, ["returned_units"])
    .join(territories, "territory_id", "left")
    .withColumn("return_rate", F.round(F.col("returned_units") / F.col("units_sold") * 100, 2))
    .withColumn("revenue_rank", F.dense_rank().over(Window.orderBy(F.desc("revenue"))))
    .select("territory_id", "region", "country", "continent", "revenue", "units_sold", "order_count",
            "returned_units", "return_rate", "revenue_rank"))

# COMMAND ----------

# STEP 6: Inspect — show the highest-revenue territories first.
display(territory_performance.orderBy("revenue_rank"))

# COMMAND ----------

# STEP 7: Write — publish territory sales and return performance.
territory_performance.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(gold_territory_performance_table)
