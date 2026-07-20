# Orchestration

Run `00_run_pipeline.py` as a Databricks Job task. It executes the layers in
dependency order:

```text
Create catalog and schemas
      ↓
Bronze ingestion
      ↓
Silver cleaning
      ↓
Gold aggregates
      ↓
Quality gate
```

If a notebook fails, the later stage does not run. For production, the lists
can be split into parallel Databricks Job tasks with the same stage-level
dependencies.
