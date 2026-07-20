# Databricks notebook source
# Shared Plotly helpers for Databricks-native dashboard notebooks.

# COMMAND ----------

# MAGIC %run ../00_setup/00_setup

# COMMAND ----------

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def gold_to_pandas(table_name):
    """Read a curated Gold table through Spark for Databricks execution."""
    return spark.table(table_name).toPandas()


def show_plotly(figure):
    """Render a Plotly figure in the Databricks notebook output cell."""
    display(figure)


def metric_cards(title, metrics):
    """Create a compact Plotly indicator row for dashboard KPI cards."""
    figure = go.Figure()
    count = len(metrics)
    for index, (label, value, prefix, suffix) in enumerate(metrics):
        figure.add_trace(go.Indicator(
            mode="number",
            value=value,
            title={"text": label},
            number={"prefix": prefix, "suffix": suffix, "valueformat": ",.2f"},
            domain={"row": 0, "column": index},
        ))
    figure.update_layout(title=title, grid={"rows": 1, "columns": count}, height=180, margin={"l": 20, "r": 20, "t": 55, "b": 10})
    return figure


def apply_style(figure, title, height=400):
    figure.update_layout(title=title, template="plotly_white", height=height, margin={"l": 40, "r": 25, "t": 55, "b": 45})
    return figure
