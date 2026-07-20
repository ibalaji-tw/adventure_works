# Bronze layer

The files ending in `.py` are Databricks source notebooks. The first line,
`# Databricks notebook source`, tells Databricks to open them as notebooks.
Each `# COMMAND ----------` separator creates a separate executable cell.

## Why use a database for Bronze?

A separate database/schema is not technically required. We now use the
`adventure_works` catalog with three schemas so the layer boundary is explicit:

```text
adventure_works.bronze
adventure_works.silver
adventure_works.gold
```

Separate schemas make permissions easier: ingestion jobs can write Bronze,
transformation jobs can read Bronze/write Silver, and analysts can receive
read-only access to Gold.

Actual tables are stored under those schemas, for example
`adventure_works.bronze.sales_raw` and `adventure_works.silver.sales_clean`.

## Incremental Sales loading

The Sales folder contains one file per year. The Sales notebook reads all files
so a newly delivered year is automatically discovered. It then checks the
existing Bronze Delta table using `(OrderNumber, OrderLineItem)` and appends
only unseen order lines. Rerunning the notebook therefore does not duplicate
historical rows. This is an idempotent batch pattern; Auto Loader would be the
next step when the folder becomes large or receives frequent files.

## Notebook pattern

Every Bronze notebook follows these visible steps:

1. Import Spark tools.
2. Define the source schema.
3. Set source and target paths.
4. Read the source file.
5. Add audit metadata.
6. Validate the landing data.
7. Create the target database.
8. Write the Bronze Delta table.
