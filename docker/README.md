# Local Spark runtime

This project uses a community Spark Docker image for local validation. It is
not a Databricks Runtime image; Unity Catalog commands and `dbutils` remain
Databricks-only features.

From the repository root, start Docker Desktop and run:

```bash
docker compose -f adventure_final_project/docker-compose.yml build
docker compose -f adventure_final_project/docker-compose.yml run --rm adventure-spark-tests
```

The first test run validates notebook structure and the real sales-file
business key. A Databricks cluster is still required to execute the notebooks
end to end because they use `%run`, `dbutils`, Unity Catalog, and DBFS paths.
