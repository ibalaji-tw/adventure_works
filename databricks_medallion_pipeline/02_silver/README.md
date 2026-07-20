# Silver layer

Each `.py` file is a Databricks notebook because it starts with
`# Databricks notebook source`. Each `# COMMAND ----------` marker creates a
separate executable cell, and every cell has a short explanation of its job.

Run the notebooks after all Bronze tables exist. Silver is where source data
becomes a consistent analytical model:

- `adventure_works.silver.customers_clean`: typed income/dates, standard names, masked email
- `adventure_works.silver.sales_clean`: typed dates/keys, deduplicated order lines, calendar columns
- `adventure_works.silver.products_clean`, `categories_clean`, `subcategories_clean`: clean dimensions
- `adventure_works.silver.product_dimension`: product hierarchy joined into one reusable dimension
- `adventure_works.silver.territories_clean`: standard territory names and masked manager email
- `adventure_works.silver.returns_clean`: typed return facts with calendar columns
