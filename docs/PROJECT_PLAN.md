# Adventure Works — DE Upskilling Final Project Plan
# (All Modules Integrated)

**Author:** Balaji S, Anuraag Khare, Hemalatha Thatigutla, Kshitija Talathi
**Dataset:** Adventure Works (Microsoft sample — fictional bicycle company)
**Goal:** Build a production-grade end-to-end data platform using every concept from the course.

---

## Business Questions (Module 01 & 12)
1. What is total revenue and order volume trend by year and month?
2. Which product categories and subcategories drive the most revenue?
3. Which territories/regions perform best in sales?
4. What is the product return rate by category — and which products are most returned?
5. Who are our top customers by lifetime value?

---

## Full Technology Stack

| Layer | Technology | Course Module |
|-------|-----------|---------------|
| File Formats | CSV, JSON, Delta (Parquet) | Module 02 |
| Processing | PySpark, Spark SQL | Module 03, 04 |
| Architecture | Medallion (Bronze/Silver/Gold) | Module 05 |
| Storage | Delta Lake (ACID, time travel, schema enforcement) | Module 02, 05 |
| Governance | Unity Catalog (Catalog → Schema → Table) | Module 11 |
| Security | PII masking, dynamic views, GRANT/REVOKE | Module 08, 11 |
| Orchestration | Databricks Jobs (DAG-based) | Module 09 |
| Visualisation | Databricks SQL Dashboard + Power BI | Module 06 |
| Data Quality | Assertions, contracts, null/range/schema checks | Module 05 |

---

## Unity Catalog Namespace (Module 11)

All tables live in a 3-level hierarchy:

```
adventure_works_catalog
├── bronze_schema
│   ├── sales_raw
│   ├── customers_raw
│   ├── products_raw
│   ├── categories_raw
│   ├── subcategories_raw
│   ├── territories_raw
│   └── returns_raw
├── silver_schema
│   ├── sales_clean
│   ├── customers_clean      ← PII masked here (Module 08)
│   ├── products_enriched    ← products + categories + subcategories joined
│   ├── territories_clean
│   └── returns_clean
└── gold_schema
    ├── sales_by_month
    ├── product_revenue
    ├── territory_summary
    ├── return_rate_analysis
    └── customer_ltv
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        RAW DATA (DBFS / Volume)                  │
│  CSV: Sales 2015/16/17, Customers, Products, Categories,         │
│       Subcategories, Territories    JSON: Returns                │
└────────────────────────┬─────────────────────────────────────────┘
                         │  Batch (Module 03)
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    BRONZE LAYER (Module 05)                       │
│  Raw ingestion → Delta Lake, schema enforced, partitioned        │
│  adventure_works_catalog.bronze_schema.*                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │  Type casting, cleaning, PII masking
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SILVER LAYER (Module 04, 05, 08)               │
│  Cleaned + typed + joined + PII masked → Delta Lake              │
│  adventure_works_catalog.silver_schema.*                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │  Aggregations, business logic
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    GOLD LAYER (Module 05)                         │
│  Business-ready aggregation tables → Delta Lake                  │
│  adventure_works_catalog.gold_schema.*                           │
└──────────────┬────────────────────────┬─────────────────────────┘
               │                        │
               ▼                        ▼
  ┌────────────────────┐    ┌──────────────────────┐
  │ Databricks SQL     │    │ Power BI              │
  │ Dashboard (Mod 06) │    │ (Partner Connect /    │
  │                    │    │  JDBC - Module 06)    │
  └────────────────────┘    └──────────────────────┘

  Orchestrated by Databricks Jobs (DAG) — Module 09
  Governed by Unity Catalog + dynamic views — Module 11
```

---

## Notebook Structure (Complete)

```
adventure_works_final_project/
│
├── notebooks/
│   │
│   ├── 00_setup/
│   │   └── 00_unity_catalog_setup.sql        ← Module 11: create catalog, schemas, grants
│   │
│   ├── 01_bronze/
│   │   ├── 01_ingest_sales_batch.py           ← Module 03: CSV read with schema, Delta write
│   │   ├── 02_ingest_customers.py             ← Module 03: CSV read, Delta write
│   │   ├── 03_ingest_products.py              ← Module 03: CSV read, Delta write
│   │   ├── 04_ingest_categories.py            ← Module 03: CSV read, Delta write
│   │   ├── 05_ingest_territories.py           ← Module 03: CSV read, Delta write
│   │   └── 06_ingest_returns.py               ← Module 03: JSON read, Delta write
│   │
│   ├── 02_silver/
│   │   ├── 01_silver_sales.py                 ← Module 04: type cast, dedup, date parse
│   │   ├── 02_silver_customers.py             ← Module 08: PII masking (email, phone)
│   │   ├── 03_silver_products_enriched.py     ← Module 04: 3-way join (products+cat+subcat)
│   │   ├── 04_silver_territories.py           ← Module 04: clean, rename columns
│   │   └── 05_silver_returns.py               ← Module 04: from_json unpack, type cast
│   │
│   ├── 03_gold/
│   │   ├── 01_gold_sales_by_month.py          ← Module 05: groupBy year/month, agg revenue
│   │   ├── 02_gold_product_revenue.py         ← Module 05: groupBy category, sum revenue
│   │   ├── 03_gold_territory_summary.py       ← Module 05: groupBy territory, rank
│   │   ├── 04_gold_return_rate.py             ← Module 05: join sales+returns, calc pct
│   │   └── 05_gold_customer_ltv.py            ← Module 05: window func, rank customers
│   │
│   ├── 04_quality/
│   │   ├── 01_quality_bronze.py               ← Module 05: schema, row count, null checks
│   │   ├── 02_quality_silver.py               ← Module 05: type checks, dedup, join verify
│   │   └── 03_quality_gold.py                 ← Module 05: range checks, business assertions
│   │
│   ├── 05_governance/
│   │   ├── 01_dynamic_views.sql               ← Module 11: row/col security on customers
│   │   └── 02_grants_and_access.sql           ← Module 11: GRANT SELECT to roles
│   │
│   └── 07_dashboard/
│       └── 01_dashboard_queries.sql           ← Module 06: Databricks SQL dashboard
│
├── tests/
│   ├── test_bronze.py                         ← Module 05: unit tests for Bronze transforms
│   ├── test_silver.py                         ← Module 05: unit tests for Silver transforms
│   └── test_gold.py                           ← Module 05: unit tests for Gold transforms
│
└── docs/
    └── PROJECT_PLAN.md                        ← This file
```

---

## Module-by-Module Implementation

---

### MODULE 01 — Notebook Header Convention
Every notebook starts with this metadata block:
```python
# Project:  Adventure Works DE Final Project
# Summary:  [What this notebook does]
# Layer:    Bronze / Silver / Gold
# Author:   Balaji
# Dataset:  Adventure Works (Microsoft sample)
```

---

### MODULE 02 — Data Architecture Decisions

**Why Delta Lake for all layers:**
- ACID transactions: safe concurrent reads/writes
- Schema enforcement: no bad data silently lands
- Time travel: `VERSION AS OF` to debug or reprocess
- Parquet underneath: columnar, compressed, fast reads

**Batch Ingestion:**
- Historical load: batch (2015–2017 CSVs already on disk)

**Orchestration DAG (Databricks Jobs):**
```
setup → bronze (parallel) → silver (parallel) → gold (parallel) → quality → dashboard
```

---

### MODULE 03 — Bronze Ingestion Pattern

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

sales_schema = StructType([
    StructField("OrderDate",      StringType(),  True),
    StructField("StockDate",      StringType(),  True),
    StructField("OrderNumber",    StringType(),  True),
    StructField("ProductKey",     IntegerType(), True),
    StructField("CustomerKey",    IntegerType(), True),
    StructField("TerritoryKey",   IntegerType(), True),
    StructField("OrderLineItem",  IntegerType(), True),
    StructField("OrderQuantity",  IntegerType(), True),
])

df = (spark.read
        .format("csv")
        .option("header", True)
        .schema(sales_schema)
        .load("/path/to/sales/"))

# Combine 3 years with union (same schema)
df_all = df_2015.union(df_2016).union(df_2017)

df_all.write.format("delta").mode("overwrite") \
    .saveAsTable("adventure_works_catalog.bronze_schema.sales_raw")
```

**Window function for dedup (latest record per order line):**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

w = Window.partitionBy("OrderNumber","OrderLineItem").orderBy(col("ingestion_ts").desc())
df.withColumn("rn", row_number().over(w)).filter(col("rn")==1).drop("rn")
```

---

### MODULE 04 — Silver Advanced Transformations

**Type casting sales:**
```python
from pyspark.sql.functions import to_date, col
df.withColumn("OrderDate", to_date(col("OrderDate"), "M/d/yyyy"))
```

**Unpack Returns JSON (from_json):**
```python
from pyspark.sql.functions import from_json
returns_schema = StructType([
    StructField("ReturnDate",   StringType(),  True),
    StructField("TerritoryKey", IntegerType(), True),
    StructField("ProductKey",   IntegerType(), True),
    StructField("ReturnQuantity", IntegerType(), True),
])
df.withColumn("data", from_json(col("body"), returns_schema)).select("data.*")
```

**3-way product join:**
```python
products.join(subcategories, "ProductSubcategoryKey", "left") \
        .join(categories,    "ProductCategoryKey",    "left") \
        .select("ProductKey","ProductName","ProductCost","ProductPrice",
                "SubcategoryName","CategoryName")
```

**Date arithmetic (days since order):**
```python
from pyspark.sql.functions import datediff, current_date
df.withColumn("days_since_order", datediff(current_date(), col("OrderDate")))
```

---

### MODULE 05 — Medallion Architecture + Data Quality

**Bronze → Silver → Gold progression:**
- Bronze: raw, schema enforced, no business logic
- Silver: cleaned, typed, joined, PII masked
- Gold: aggregated, business-ready, tested

**Data quality checks (run in 04_quality/):**
```python
# Schema check
def assert_schema(df, expected_cols):
    missing = set(expected_cols) - set(df.columns)
    assert not missing, f"Missing columns: {missing}"

# Null check
def assert_no_nulls(df, key_cols):
    for c in key_cols:
        n = df.filter(col(c).isNull()).count()
        assert n == 0, f"Column {c} has {n} nulls"

# Row count check
def assert_row_count(df, min_rows):
    n = df.count()
    assert n >= min_rows, f"Expected >= {min_rows} rows, got {n}"

# Range check (Gold)
def assert_range(df, column, lo, hi):
    bad = df.filter((col(column) < lo) | (col(column) > hi)).count()
    assert bad == 0, f"{column} has {bad} rows out of range [{lo},{hi}]"

# Join key uniqueness before joining
def assert_unique_key(df, key_col):
    dupes = df.groupBy(key_col).count().filter(col("count") > 1).count()
    assert dupes == 0, f"Key {key_col} has {dupes} duplicate values"
```

**Unit test pattern (from Module 5 tests folder):**
```python
def test_silver_sales_date_cast(spark):
    input_data = [("1/1/2015",), ("12/31/2017",)]
    df = spark.createDataFrame(input_data, ["OrderDate"])
    result = df.transform(cast_order_date)
    assert result.schema["OrderDate"].dataType == DateType()
    print("All tests pass!")
```

---

### MODULE 06 — Visualisation

**Databricks SQL Dashboard (notebook 07_dashboard/):**
- Line chart: Monthly revenue 2015–2017
- Bar chart: Revenue by product category
- Bar chart: Top 10 territories by revenue
- KPI tiles: Total revenue, total orders, avg order value, return rate
- Table: Top 10 customers by lifetime value

**Power BI Connection:**
- Databricks Partner Connect → Power BI Direct Query
- Connect to `adventure_works_catalog.gold_schema.*`
- Build star schema: `gold_sales_by_month` as fact, dims from Silver

---

### MODULE 08 — Data Security & PII Masking

**Customer PII columns to mask in Silver:**
- `EmailAddress` → mask all but domain: `user@domain.com` → `***@domain.com`
- `Phone` → keep last 4 digits: `555-123-4567` → `***-***-4567`
- `Prefix` / `BirthDate` → keep as-is (not sensitive)

```python
from pyspark.sql.functions import concat, lit, regexp_extract, col

# Mask email: keep domain only
df.withColumn("EmailAddress",
    concat(lit("***@"), regexp_extract(col("EmailAddress"), "@(.+)", 1)))

# Mask phone: keep last 4
df.withColumn("Phone",
    concat(lit("***-***-"), regexp_extract(col("Phone"), r'(\d{4})$', 1)))
```

---

### MODULE 09 — Infrastructure & Orchestration

**Databricks Jobs DAG (all notebooks wired as tasks):**
```
Task 1: 00_unity_catalog_setup.sql
    ↓
Task 2a: 01_ingest_sales_batch.py    ← parallel
Task 2b: 02_ingest_customers.py      ← parallel
Task 2c: 03_ingest_products.py       ← parallel
Task 2d: 06_ingest_returns.py        ← parallel
    ↓
Task 3a: 01_silver_sales.py          ← parallel
Task 3b: 02_silver_customers.py      ← parallel
Task 3c: 03_silver_products.py       ← parallel
    ↓
Task 4a: 01_gold_sales_by_month.py   ← parallel
Task 4b: 02_gold_product_revenue.py  ← parallel
Task 4c: 05_gold_customer_ltv.py     ← parallel
    ↓
Task 5: 03_quality_gold.py           ← quality gate (blocks dashboard)
    ↓
Task 6: 01_dashboard_queries.sql
```

---

### MODULE 10 — Databricks Platform

- Use Databricks SQL Warehouse for Gold layer queries (not all-purpose cluster)
- Use Databricks Notebooks for development
- Use Databricks Jobs for scheduled/orchestrated runs
- SQL Warehouse powers both Databricks dashboard AND Power BI connection

---

### MODULE 11 — Data Governance (Unity Catalog)

**Setup notebook (00_unity_catalog_setup.sql):**
```sql
-- Create the top-level catalog
CREATE CATALOG IF NOT EXISTS adventure_works_catalog;
USE CATALOG adventure_works_catalog;

-- Create schemas per layer
CREATE SCHEMA IF NOT EXISTS bronze_schema;
CREATE SCHEMA IF NOT EXISTS silver_schema;
CREATE SCHEMA IF NOT EXISTS gold_schema;

-- Grant read access on gold to analysts
GRANT USAGE ON CATALOG adventure_works_catalog TO `account users`;
GRANT USAGE ON SCHEMA gold_schema TO `account users`;
GRANT SELECT ON ALL TABLES IN SCHEMA gold_schema TO `account users`;

-- Restrict silver (has masked PII — analysts see dynamic view, not raw)
GRANT SELECT ON VIEW silver_schema.customers_safe_view TO `account users`;
```

**Dynamic view — hide raw PII from non-admin roles:**
```sql
CREATE OR REPLACE VIEW silver_schema.customers_safe_view AS
SELECT
  CustomerKey,
  CASE WHEN is_account_group_member('admins')
       THEN EmailAddress
       ELSE CONCAT('***@', SPLIT(EmailAddress,'@')[1])
  END AS EmailAddress,
  CASE WHEN is_account_group_member('admins')
       THEN Phone
       ELSE CONCAT('***-***-', RIGHT(Phone,4))
  END AS Phone,
  FirstName, LastName, BirthDate, AnnualIncome, TotalChildren, Country
FROM silver_schema.customers_clean;
```

**Custom masking function:**
```sql
CREATE OR REPLACE FUNCTION silver_schema.mask_string(x STRING)
  RETURNS STRING
  RETURN CONCAT(REPEAT('*', LENGTH(x) - 4), RIGHT(x, 4));
```

---

### MODULE 12 — Final Project Requirements Met

| Requirement | Where in this project |
|-------------|----------------------|
| Dataset with clear business questions | 5 defined business questions above |
| Bronze → Silver → Gold | 15 notebooks across 3 layers |
| Data quality gates | 04_quality/ folder, assertions in every Gold notebook |
| Visualisation | 07_dashboard/ (Databricks SQL) + Power BI |
| Power BI | Gold tables connected via Partner Connect |
| Security & PII | Module 08 masking in Silver + Module 11 dynamic views |
| Governance | Module 11 Unity Catalog, GRANTs, views |
| Orchestration | Databricks Jobs DAG (Module 09) |
| Notebook documentation | Module 01 header in every notebook |
| Presentation | All 5 business questions answered with visuals |

---

## Implementation Order

| Step | Notebook | Module | Deliverable |
|------|----------|--------|-------------|
| 1 | `00_unity_catalog_setup.sql` | 11 | Catalog + schemas + grants |
| 2 | `01_bronze/01_ingest_sales_batch.py` | 03 | Sales 2015-17 in Bronze Delta |
| 3 | `01_bronze/02-06` | 03 | All dims + returns in Bronze |
| 4 | `02_silver/01_silver_sales.py` | 04 | Clean typed sales |
| 5 | `02_silver/02_silver_customers.py` | 08 | PII-masked customers |
| 6 | `02_silver/03_silver_products.py` | 04 | 3-way joined product dim |
| 7 | `02_silver/04-05` | 04 | Territories + Returns Silver |
| 8 | `03_gold/01-05` | 05 | All 5 Gold agg tables |
| 9 | `04_quality/01-03` | 05 | All quality assertions pass |
| 10 | `05_governance/01-02` | 11 | Dynamic views + access control |
| 11 | `07_dashboard/01` | 06 | Databricks SQL Dashboard live |
| 12 | Power BI | 06 | BI visuals from Gold tables |
