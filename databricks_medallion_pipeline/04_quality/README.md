# Quality gate

`01_quality_gate.py` must be the final task before dashboards are refreshed.
It checks:

- Required Silver and Gold tables exist and contain rows.
- Dimension keys are unique.
- Sales order lines are deduplicated.
- Sales and returns quantities are positive.
- Sales foreign keys resolve to Silver dimensions.
- Gold revenue and return-rate values are in valid ranges.
- Gold monthly revenue reconciles to the Silver sales fact.

The detailed audit output is written to `adventure_works.gold.quality_results`.
