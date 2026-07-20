"""Checks the real sales files without requiring Spark or pandas."""
import csv
from collections import Counter
from pathlib import Path


SALES_DIR = Path(__file__).parents[1] / "data" / "sales"


def read_sales():
    rows = []
    for path in sorted(SALES_DIR.glob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def test_sales_line_key_is_unique_in_source():
    rows = read_sales()
    assert len(rows) == 56046
    keys = [(row["OrderNumber"], row["OrderLineItem"]) for row in rows]
    assert len(keys) == len(set(keys))


def test_order_number_is_not_the_sales_line_key():
    rows = read_sales()
    counts = Counter(row["OrderNumber"] for row in rows)
    assert len(counts) == 25164
    assert max(counts.values()) == 8
