# Databricks notebook source
# MAGIC %run ../00_setup/00_setup

# Quality gate — run after Silver and Gold have been built.

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

from datetime import datetime
from pyspark.sql import functions as F

results = []

def check(name, condition, detail):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail, datetime.utcnow().isoformat()))
    if not condition:
        print(f"FAIL: {name} — {detail}")
    else:
        print(f"PASS: {name}")

def table(name):
    return spark.table(f"{catalog_name}.{name}")

# 1. Required tables exist and are not empty.
required_tables = [
    "silver.customers_clean", "silver.sales_clean", "silver.product_dimension", "silver.territories_clean", "silver.returns_clean",
    "gold.sales_by_month", "gold.product_performance", "gold.customer_value",
    "gold.territory_performance", "gold.return_by_product",
]
for name in required_tables:
    try:
        count = table(name).count()
        check(f"table_exists_and_nonempty:{name}", count > 0, f"row_count={count}")
    except Exception as error:
        check(f"table_exists_and_nonempty:{name}", False, str(error))

# 2. Key and duplicate checks on Silver.
customers = table("silver.customers_clean")
sales = table("silver.sales_clean")
products = table("silver.product_dimension")
territories = table("silver.territories_clean")
returns = table("silver.returns_clean")

check("customers_unique_key", customers.select("customer_id").distinct().count() == customers.count(), "duplicate customer_id")
check("products_unique_key", products.select("product_id").distinct().count() == products.count(), "duplicate product_id")
check("territories_unique_key", territories.select("territory_id").distinct().count() == territories.count(), "duplicate territory_id")
check("sales_unique_order_line", sales.select("order_number", "order_line_item").distinct().count() == sales.count(), "duplicate order line")

# 3. Null, quantity, and referential-integrity checks.
check("sales_no_null_keys", sales.filter(
    F.col("product_id").isNull() | F.col("customer_id").isNull() | F.col("territory_id").isNull()).limit(1).count() == 0,
      "null foreign key in sales")
check("sales_positive_quantity", sales.filter(F.col("order_quantity") <= 0).limit(1).count() == 0, "non-positive quantity")
check("returns_positive_quantity", returns.filter(F.col("return_quantity") <= 0).limit(1).count() == 0, "non-positive return quantity")
check("sales_products_join", sales.select("product_id").distinct().join(products.select("product_id"), "product_id", "left_anti").count() == 0,
      "sales product key not found in product dimension")
check("sales_customers_join", sales.select("customer_id").distinct().join(customers.select("customer_id"), "customer_id", "left_anti").count() == 0,
      "sales customer key not found in customers")
check("sales_territories_join", sales.select("territory_id").distinct().join(territories.select("territory_id"), "territory_id", "left_anti").count() == 0,
      "sales territory key not found in territories")

# 4. Gold metric ranges and reconciliation.
monthly = table("gold.sales_by_month")
return_products = table("gold.return_by_product")
check("gold_revenue_nonnegative", monthly.filter(F.col("revenue") < 0).limit(1).count() == 0, "negative monthly revenue")
check("gold_return_rate_range", return_products.filter(
    (F.col("return_rate_pct") < 0) | (F.col("return_rate_pct") > 100)).limit(1).count() == 0,
      "return rate outside 0-100")

silver_revenue = (sales.join(products.select("product_id", "product_price"), "product_id")
    .select(F.sum(F.col("order_quantity") * F.col("product_price")).alias("value")).first()["value"])
gold_revenue = monthly.select(F.sum("revenue").alias("value")).first()["value"]
check("gold_revenue_reconciles", abs(float(silver_revenue or 0) - float(gold_revenue or 0)) < 0.01,
      f"silver={silver_revenue}, gold={gold_revenue}")

report = spark.createDataFrame(results, ["check_name", "status", "detail", "checked_at"])
display(report)
report.write.format("delta").mode("overwrite").saveAsTable(quality_results_table)

failed = report.filter(F.col("status") == "FAIL").count()
if failed:
    raise RuntimeError(f"Quality gate failed with {failed} failing checks")
print("QUALITY GATE PASSED")
