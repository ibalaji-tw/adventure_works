# Databricks notebook source
# Gold 03 — Customer lifetime value and customer segments.

# COMMAND ----------

# STEP 0: Configuration — load shared source and destination names.
# MAGIC %run ../00_setup/00_setup

# STEP 1: Imports — load aggregation and ranking functions.
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# STEP 2: Read — load Silver sales, products, and customer dimensions.
sales = spark.table(silver_sales_table)
products = spark.table(silver_product_dimension_table)
customers = spark.table(silver_customers_table)

# COMMAND ----------

# STEP 3: Calculate customer value — sum revenue and count customer orders.
customer_value = (sales.join(products.select("product_id", "product_price"), "product_id", "left")
    .withColumn("revenue", F.col("order_quantity") * F.col("product_price"))
    .groupBy("customer_id")
    .agg(F.countDistinct("order_number").alias("order_count"), F.sum("order_quantity").alias("units_purchased"),
         F.round(F.sum("revenue"), 2).alias("lifetime_value"), F.max("order_date").alias("last_order_date"))
    .join(customers.select("customer_id", "full_name", "gender", "annual_income", "occupation", "education_level"),
          "customer_id", "left"))

# COMMAND ----------

# STEP 4: Define threshold — use the 75th percentile as the High Value cutoff.
threshold = customer_value.agg(F.expr("percentile_approx(lifetime_value, 0.75)").alias("high_value_threshold"))

# COMMAND ----------

# STEP 5: Segment and rank — classify customers and rank by lifetime value.
customer_segments = (customer_value.crossJoin(threshold)
    .withColumn("customer_segment", F.when(F.col("lifetime_value") >= F.col("high_value_threshold"), "High Value")
        .when(F.col("order_count") >= 2, "Repeat")
        .otherwise("Standard"))
    .withColumn("lifetime_value_rank", F.dense_rank().over(Window.orderBy(F.desc("lifetime_value"))))
    .drop("high_value_threshold"))

# COMMAND ----------

# STEP 6: Validate and inspect — every customer value row needs a customer key.
assert customer_segments.filter(F.col("customer_id").isNull()).limit(1).count() == 0
display(customer_segments.orderBy("lifetime_value_rank").limit(20))

# COMMAND ----------

# STEP 7: Write customers — publish customer-level lifetime value.
customer_segments.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(gold_customer_value_table)

# COMMAND ----------

# STEP 8: Aggregate segments — summarize customer counts and value.
segment_summary = (customer_segments.groupBy("customer_segment")
    .agg(F.count("customer_id").alias("customer_count"), F.round(F.sum("lifetime_value"), 2).alias("revenue"),
         F.round(F.avg("lifetime_value"), 2).alias("average_customer_value"))
    .orderBy(F.desc("revenue")))
display(segment_summary)

# COMMAND ----------

# STEP 9: Write segments — publish the segment summary table.
segment_summary.write.format("delta").mode("overwrite").saveAsTable(gold_customer_segments_table)
