# Adventure Works Final Project

This project is built from scratch using the complete Adventure Works dataset.

## Main implementation

The `from_scratch` folder contains the complete Databricks implementation:

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

The source dataset remains in the sibling `adventure-spark/Dataset` folder.
Run the single setup notebook `from_scratch/00_setup/00_setup.py` first, then run the pipeline
from `from_scratch/05_orchestration/00_run_pipeline.py`.
