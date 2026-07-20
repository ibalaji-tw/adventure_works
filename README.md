# Adventure Works Final Project

This project is built from scratch using the complete Adventure Works dataset.

## Main implementation

The `databricks_medallion_pipeline` folder contains the complete Databricks implementation:

```text
00_setup       Create adventure_works catalog and layer schemas
01_bronze      Ingest source files into Bronze Delta tables
02_silver      Clean, standardize, and enrich data
03_gold        Build business marts and insights
04_quality     Run data-quality checks and reconciliation
05_orchestration Run the full pipeline in dependency order
06_dashboard   Dashboard SQL queries
```

## Catalog structure

```text
adventure_works.bronze
adventure_works.silver
adventure_works.gold
```

The complete source dataset is included in the repository under `data/`, including the
year-partitioned sales files and returns JSON. In Databricks, upload this folder to the
configured DBFS source location before running ingestion.

Run the single setup notebook `databricks_medallion_pipeline/00_setup/00_setup.py` first,
then run the pipeline from `databricks_medallion_pipeline/05_orchestration/00_run_pipeline.py`.
