-- Dashboard queries over the Databricks Medallion Gold tables.
USE CATALOG adventure_works;
USE SCHEMA gold;

-- KPI cards
SELECT SUM(revenue) AS total_revenue, SUM(order_count) AS total_orders,
       SUM(units_sold) AS total_units, SUM(gross_profit) AS total_gross_profit
FROM sales_by_month;

-- Revenue trend
SELECT order_month_start, revenue, order_count, active_customers, gross_margin_pct
FROM sales_by_month ORDER BY order_month_start;

-- Product profitability
SELECT product_name, category_name, subcategory_name, revenue, gross_profit, gross_margin_pct
FROM product_performance ORDER BY profit_rank LIMIT 20;

-- Customer segments
SELECT customer_segment, customer_count, revenue, average_customer_value
FROM customer_segments ORDER BY revenue DESC;

-- Territory performance
SELECT region, country, continent, revenue, return_rate, revenue_rank
FROM territory_performance ORDER BY revenue_rank;

-- Return hotspots
SELECT product_name, category_name, subcategory_name, sold_units, returned_units, return_rate_pct
FROM return_by_product ORDER BY return_rate_pct DESC LIMIT 20;
