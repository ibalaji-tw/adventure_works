# Databricks Medallion pipeline build order

This folder is the clean, incremental implementation. Each notebook is small
enough to understand and review before moving to the next layer.

## Design decisions

1. Bronze keeps source column names and source values so the original data can
   be replayed and audited.
2. Silver owns data cleaning, standard names, type conversions, joins, and PII
   protection.
3. Gold owns business definitions and aggregations only.
4. Every notebook reads one clear input, shows a small validation result, and
   writes one Delta table.

The project uses one Unity Catalog named `adventure_works` with three layer
schemas: `adventure_works.bronze`, `adventure_works.silver`, and
`adventure_works.gold`. Run `00_setup/00_setup.py` first.

`00_setup/00_setup.py` is the single setup notebook. It creates the catalog and
schemas, then contains all source paths, destination table names, catalog/schema
names, and the workspace orchestration path. Every Bronze, Silver, Gold,
quality, and orchestration notebook loads it as the first command in its first
cell with `# MAGIC %run ../00_setup/00_setup`. Keeping `%run` first prevents
Databricks from interpreting it as an IPython line magic.

## Build order

1. `01_bronze/01_ingest_customers.py`
2. `01_bronze/02_ingest_sales.py`
3. Remaining Bronze source notebooks: products, categories, subcategories,
   territories, returns
4. Silver notebooks for each cleaned entity and the conformed sales fact
5. Gold notebooks for sales, product, territory, returns, and customer insights
6. `04_quality/01_quality_gate.py`
7. `05_orchestration/00_run_pipeline.py`
8. `06_dashboard/01_dashboard_queries.sql`
