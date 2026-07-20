---
title: "Management Summary"
subtitle: "Adventure Works — End-to-End Data Engineering Platform"
author: "Balaji S, Anuraag Khare, Hemalatha Thatigutla, Kshitija Talathi"
date: "July 2026"
---

# Management Summary

**Team / Author:** Balaji S, Anuraag Khare, Hemalatha Thatigutla, Kshitija Talathi

---

## Dataset

**Name:** Adventure Works (Microsoft Sample Dataset)

**Description:**
Adventure Works is a fictional mid-sized bicycle manufacturer and retailer used as Microsoft's canonical sample dataset. It covers multi-year transactional sales data (2015–2017) across seven interrelated entities: Sales, Customers, Products, Product Categories, Product Subcategories, Sales Territories, and Returns. The dataset is deliberately multi-source (CSV + Excel + JSON) and multi-year, making it ideal for demonstrating real-world data engineering patterns such as schema enforcement, historical batch loads, and cross-table enrichment.

| Entity | Format | Approx. Records |
|--------|--------|-----------------|
| Sales (2015, 2016, 2017) | CSV | ~56,000 orders |
| Customers | CSV | ~18,000 customers |
| Products | Excel (XLSX) | ~293 products |
| Product Categories | Excel (XLSX) | 4 categories |
| Product Subcategories | Excel (XLSX) | 17 subcategories |
| Sales Territories | CSV | 10 territories |
| Returns | JSON | ~1,800 return events |

---

## Project Hypothesis

A bicycle retail business generates rich transactional data across sales, customers, products, and territories. However, raw data scattered across flat CSV, Excel, and JSON files cannot support reliable business reporting without a structured transformation pipeline.

**Hypothesis:** By applying a Medallion Architecture (Bronze → Silver → Gold) on top of Databricks and Delta Lake — with automated quality gates, PII masking, and role-based governance — it is possible to turn raw Adventure Works files into a fully governed, dashboard-ready analytics platform that answers five critical business questions with confidence.

The platform proves that data quality, security, and scalability are not afterthoughts but foundational design decisions embedded at every layer.

---

## Key Business Questions

1. **Revenue Trend** — What is total revenue and order volume by year and month?
2. **Product Performance** — Which product categories and subcategories drive the most revenue?
3. **Territory Analysis** — Which sales territories and regions perform best?
4. **Return Rate** — What is the product return rate by category, and which products are returned most?
5. **Customer Lifetime Value** — Who are our top customers by lifetime spending?

---

## Architecture & Technology Stack

The platform follows the **Medallion Architecture** (three-layer data lakehouse) built entirely on Databricks and Delta Lake:

```
Raw Files (CSV + Excel + JSON)
        │
        ▼
   Batch Load (PySpark)
                │
                ▼
        BRONZE LAYER — Raw ingestion, schema enforcement, Delta Lake
                │
                ▼
        SILVER LAYER — Type casting, deduplication, joins, PII masking
                │
                ▼
        GOLD LAYER — Business aggregations, KPI tables, quality-gated
                │
        ┌───────┴───────┐
        ▼               ▼
  Databricks SQL    Power BI
  Dashboard         (Direct Query)
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Storage & Processing | Delta Lake + PySpark | ACID transactions, time travel, schema enforcement |
| Batch Ingestion | PySpark CSV/Excel/JSON Reader | Historical load of 3-year sales + all dimension tables |
| Transformations | PySpark + Spark SQL | Type casting, joins, window functions, aggregations |
| Governance | Unity Catalog | 3-level namespace, GRANT/REVOKE, dynamic views |
| Security | PII Masking + Dynamic Views | Email and phone redacted in Silver; role-based access in Gold |
| Orchestration | Databricks Jobs (DAG) | Parallel task execution across Bronze → Silver → Gold |
| Data Quality | Custom Assertion Framework | Schema, null, range, uniqueness checks at every layer |
| Visualisation | Databricks SQL Dashboard + Power BI | Production-grade reporting |

---

## Unity Catalog Namespace

All tables are governed under a three-level hierarchy in Databricks Unity Catalog:

```
adventure_works_catalog
├── bronze_schema       (raw ingestion — 7 tables)
├── silver_schema       (cleaned + joined — 5 tables + 1 secure view)
└── gold_schema         (business aggregates — 5 KPI tables)
```

Analysts receive **SELECT on Gold only**. Silver PII columns are accessible exclusively through a dynamic view that masks email and phone for non-admin roles.

---

## Data Quality Strategy

A dedicated quality notebook layer (`04_quality/`) runs **before** the dashboard is populated, acting as a hard gate:

- **Schema checks** — assert all expected columns exist at every layer
- **Null checks** — key join columns (ProductKey, CustomerKey, TerritoryKey) must have zero nulls in Silver
- **Row count assertions** — Gold tables must meet minimum row thresholds
- **Range checks** — revenue and quantity values must fall within business-valid bounds
- **Uniqueness checks** — dimension key columns validated before joins to prevent fan-out

The orchestration DAG is wired so that the dashboard notebook only runs if all quality assertions pass.

---

## Security & PII Handling

Customer PII is handled in two stages:

1. **Silver Layer (Notebook)** — `EmailAddress` is masked to `***@domain.com`; `Phone` is masked to `***-***-4567` using PySpark regex transforms.
2. **Dynamic View (Unity Catalog)** — A `customers_safe_view` uses `is_account_group_member('admins')` to show full data only to privileged roles; all other users see the masked version.

This two-layer approach ensures PII protection holds both at the data level and at the query/access level.

---

## Orchestration Pipeline (Databricks Jobs)

The pipeline is fully orchestrated as a DAG with six phases:

```
Setup → Bronze (parallel) → Silver (parallel) → Gold (parallel) → Quality Gate → Dashboard
```

Total notebooks: **15** (13 Python/SQL pipeline notebooks + 2 quality/governance). Parallel execution within each phase reduces end-to-end latency.

---

## Final Outcomes & Deliverables

| Deliverable | Description |
|-------------|-------------|
| Bronze Delta tables (7) | Raw ingestion, schema enforced, partitioned, audit-ready |
| Silver Delta tables (5) | Typed, deduplicated, PII-masked, joined business entities |
| Gold KPI tables (5) | Revenue by month, product revenue, territory summary, return rate, customer LTV |
| Data quality report | Automated assertions passing across all 3 layers |
| Databricks SQL Dashboard | 5 live charts + 4 KPI tiles answering all business questions |
| Power BI connection | Gold tables exposed via Partner Connect for self-service BI |
| Unity Catalog governance | Full lineage, GRANTs, dynamic PII views |
| Unit tests (3 suites) | Bronze, Silver, Gold transform logic tested |

---

## Key Insights (Illustrative)

- **Revenue is concentrated in Q4** — Holiday season orders dominate year-over-year trends across 2015–2017
- **Bikes drive 90%+ of revenue** — Accessories and Clothing are high-volume but low-margin
- **North America leads territories** — US territories account for the majority of sales; Europe shows growth potential
- **Return rate is low but category-specific** — Bikes have the lowest return rate; Accessories have the highest
- **Top 100 customers drive disproportionate LTV** — Classic 80/20 pattern holds across all three years

---

## Team

- **Balaji S**
- **Anuraag Khare**
- **Hemalatha Thatigutla**
- **Kshitija Talathi**

DE Upskilling Final Project | Adventure Works Dataset | July 2026
