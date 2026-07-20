"""Runtime-independent checks for the Databricks notebook source files."""
from pathlib import Path


PROJECT = Path(__file__).parents[1]
PIPELINE = PROJECT / "databricks_medallion_pipeline"
LAYER_DIRS = [
    PIPELINE / "01_bronze",
    PIPELINE / "02_silver",
    PIPELINE / "03_gold",
]


def test_layer_notebooks_have_databricks_headers_and_cells():
    notebooks = [path for directory in LAYER_DIRS for path in directory.glob("*.py")]
    assert len(notebooks) == 17
    for notebook in notebooks:
        text = notebook.read_text()
        assert text.startswith("# Databricks notebook source"), notebook
        assert "# COMMAND ----------" in text, notebook
        assert "# STEP " in text, notebook


def test_all_layer_notebooks_load_shared_setup():
    notebooks = [path for directory in LAYER_DIRS for path in directory.glob("*.py")]
    for notebook in notebooks:
        assert "# MAGIC %run ../00_setup/00_setup" in notebook.read_text(), notebook


def test_setup_contains_all_layer_names_and_source_root():
    setup = (PIPELINE / "00_setup" / "00_setup.py").read_text()
    assert 'catalog_name = "adventure_works"' in setup
    assert 'source_root = "dbfs:/FileStore/adventure"' in setup
    for layer in ("bronze", "silver", "gold"):
        assert f".{layer}" in setup
