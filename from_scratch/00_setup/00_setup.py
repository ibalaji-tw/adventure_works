# Databricks notebook source
# Single setup notebook for catalog creation and project configuration.

# STEP 1: Create the catalog and Medallion schemas.
# This must run before any Bronze, Silver, or Gold table is written.
catalog_name = "adventure_works"
spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.bronze")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.silver")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.gold")

# COMMAND ----------

# STEP 2: Project location — change this when uploading the project elsewhere.
workspace_base_path = "/Workspace/Shared/adventure_final_project/from_scratch"

# COMMAND ----------

# STEP 3: Source location — all source files live below this root folder.
source_root = "dbfs:/FileStore/adventure"
customers_source_path = f"{source_root}/AdventureWorks-Customers.csv"
sales_source_path = f"{source_root}/sales/"
products_source_path = f"{source_root}/AdventureWorks_Products.csv"
categories_source_path = f"{source_root}/AdventureWorks_Product_Categories.csv"
subcategories_source_path = f"{source_root}/AdventureWorks_Product_Subcategories.csv"
territories_source_path = f"{source_root}/AdventureWorks-Territories.csv"
returns_source_path = f"{source_root}/AdventureWorks_Returns.json"

# COMMAND ----------

# STEP 4: Layer schemas — define the three Medallion layers once.
bronze_schema = f"{catalog_name}.bronze"
silver_schema = f"{catalog_name}.silver"
gold_schema = f"{catalog_name}.gold"

# COMMAND ----------

# STEP 5: Bronze destinations — raw source-shaped Delta tables.
bronze_customers_table = f"{bronze_schema}.customers_raw"
bronze_sales_table = f"{bronze_schema}.sales_raw"
bronze_products_table = f"{bronze_schema}.products_raw"
bronze_categories_table = f"{bronze_schema}.categories_raw"
bronze_subcategories_table = f"{bronze_schema}.subcategories_raw"
bronze_territories_table = f"{bronze_schema}.territories_raw"
bronze_returns_table = f"{bronze_schema}.returns_raw"

# COMMAND ----------

# STEP 6: Silver destinations — cleaned and conformed Delta tables.
silver_customers_table = f"{silver_schema}.customers_clean"
silver_sales_table = f"{silver_schema}.sales_clean"
silver_products_table = f"{silver_schema}.products_clean"
silver_categories_table = f"{silver_schema}.categories_clean"
silver_subcategories_table = f"{silver_schema}.subcategories_clean"
silver_product_dimension_table = f"{silver_schema}.product_dimension"
silver_territories_table = f"{silver_schema}.territories_clean"
silver_returns_table = f"{silver_schema}.returns_clean"

# COMMAND ----------

# STEP 7: Gold destinations — business-ready analytical tables.
gold_sales_by_month_table = f"{gold_schema}.sales_by_month"
gold_product_performance_table = f"{gold_schema}.product_performance"
gold_category_performance_table = f"{gold_schema}.category_performance"
gold_customer_value_table = f"{gold_schema}.customer_value"
gold_customer_segments_table = f"{gold_schema}.customer_segments"
gold_territory_performance_table = f"{gold_schema}.territory_performance"
gold_return_by_product_table = f"{gold_schema}.return_by_product"
gold_return_by_category_table = f"{gold_schema}.return_by_category"
quality_results_table = f"{gold_schema}.quality_results"

# COMMAND ----------

# STEP 8: Configuration check — display the active project locations.
print(f"Catalog: {catalog_name}")
print(f"Source root: {source_root}")
print(f"Bronze schema: {bronze_schema}")
print(f"Silver schema: {silver_schema}")
print(f"Gold schema: {gold_schema}")
