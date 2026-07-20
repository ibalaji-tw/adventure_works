# Databricks notebook source
# Simple dependency-aware orchestration for the Databricks Medallion project.
# Update this once after uploading the folder to your workspace.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

# STEP 0: Configuration — shared setup was loaded at the start of this notebook.

base_path = workspace_base_path

# STEP 1: Create the catalog and Bronze/Silver/Gold schemas.
dbutils.notebook.run(f"{base_path}/00_setup/00_setup", 0)

bronze_tasks = [
    "01_bronze/01_ingest_customers",
    "01_bronze/02_ingest_sales",
    "01_bronze/03_ingest_products",
    "01_bronze/04_ingest_categories",
    "01_bronze/05_ingest_subcategories",
    "01_bronze/06_ingest_territories",
    "01_bronze/07_ingest_returns",
]
silver_tasks = [
    "02_silver/01_clean_customers",
    "02_silver/02_clean_sales",
    "02_silver/03_clean_products",
    "02_silver/04_clean_territories",
    "02_silver/05_clean_returns",
]
gold_tasks = [
    "03_gold/01_sales_summary",
    "03_gold/02_product_performance",
    "03_gold/03_customer_value",
    "03_gold/04_territory_performance",
    "03_gold/05_return_analysis",
]

def run_stage(stage_name, tasks):
    print(f"Starting {stage_name}")
    for task in tasks:
        result = dbutils.notebook.run(f"{base_path}/{task}", 0)
        print(f"Completed {task}: {result}")

# STEP 2: Ingest source files into Bronze.
run_stage("BRONZE", bronze_tasks)
# STEP 3: Clean and conform Bronze data into Silver.
run_stage("SILVER", silver_tasks)
# STEP 4: Build business aggregates in Gold.
run_stage("GOLD", gold_tasks)
# STEP 5: Stop the pipeline if any quality rule fails.
dbutils.notebook.run(f"{base_path}/04_quality/01_quality_gate", 0)
print("Adventure Works pipeline completed successfully")
