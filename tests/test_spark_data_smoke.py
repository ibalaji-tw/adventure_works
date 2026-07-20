"""Small real-Spark smoke test against the complete source dataset."""
import os
from pathlib import Path

import pytest

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, IntegerType


DATA_ROOT = Path(os.environ.get("ADVENTURE_DATA_ROOT", "/workspace/adventure_final_project/data"))


@pytest.fixture(scope="session")
def spark():
    session = (SparkSession.builder.master("local[2]")
               .appName("adventure-works-smoke-test")
               .config("spark.ui.enabled", "false")
               .config("spark.driver.bindAddress", "127.0.0.1")
               .getOrCreate())
    yield session
    session.stop()


def test_spark_reads_sales_and_builds_revenue(spark):
    schema = StructType([
        StructField("OrderDate", StringType(), True), StructField("StockDate", StringType(), True),
        StructField("OrderNumber", StringType(), True), StructField("ProductKey", IntegerType(), True),
        StructField("CustomerKey", IntegerType(), True), StructField("TerritoryKey", IntegerType(), True),
        StructField("OrderLineItem", IntegerType(), True), StructField("OrderQuantity", IntegerType(), True),
    ])
    sales = spark.read.option("header", True).schema(schema).csv(str(DATA_ROOT / "sales" / "*.csv"))
    products = spark.read.option("header", True).option("inferSchema", True).csv(
        str(DATA_ROOT / "AdventureWorks_Products.csv"))

    assert sales.count() == 56046
    assert sales.select("OrderNumber", "OrderLineItem").distinct().count() == 56046

    revenue = (sales.join(products.select("ProductKey", "ProductPrice"), "ProductKey")
        .select((sales.OrderQuantity * products.ProductPrice).alias("revenue"))
        .agg({"revenue": "sum"}).first()[0])
    assert revenue is not None
    assert revenue > 0
