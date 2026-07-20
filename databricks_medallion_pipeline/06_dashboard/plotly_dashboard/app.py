"""Adventure Works three-page Plotly Dash dashboard.

Run locally with the included source data, or set ADVENTURE_DATA_ROOT to a
different data location. The calculations mirror the Gold-layer definitions:
revenue, gross profit, customer value, and High Value/Repeat/Standard segments.
"""
from pathlib import Path
import os

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table


DATA_ROOT = Path(os.environ.get("ADVENTURE_DATA_ROOT", Path(__file__).parents[3] / "data"))
COLORS = {"teal": "#00AFA5", "navy": "#263238", "gold": "#F2C94C", "red": "#FF6B6B"}


def load_data():
    """Load and conform the source files for the companion dashboard."""
    customers = pd.read_csv(DATA_ROOT / "AdventureWorks_Customers.csv", sep="|")
    products = pd.read_csv(DATA_ROOT / "AdventureWorks_Products.csv")
    categories = pd.read_csv(DATA_ROOT / "AdventureWorks_Product_Categories.csv")
    subcategories = pd.read_csv(DATA_ROOT / "AdventureWorks_Product_Subcategories.csv")
    sales = pd.concat(
        [pd.read_csv(path) for path in sorted((DATA_ROOT / "sales").glob("*.csv"))],
        ignore_index=True,
    )
    returns = pd.read_json(DATA_ROOT / "AdventureWorks_Returns.json")

    customers = customers.rename(columns={"CustomerKey": "customer_id", "Gender": "gender", "Occupation": "occupation"})
    customers["annual_income"] = pd.to_numeric(customers["AnnualIncome"], errors="coerce")
    customers["full_name"] = customers["FirstName"].fillna("") + " " + customers["LastName"].fillna("")
    products = products.rename(columns={"ProductKey": "product_id", "ProductName": "product_name", "ProductPrice": "product_price", "ProductCost": "product_cost"})
    products = products.merge(subcategories, on="ProductSubcategoryKey", how="left").merge(categories, on="ProductCategoryKey", how="left")
    products = products.rename(columns={"CategoryName": "category_name", "SubcategoryName": "subcategory_name"})
    sales = sales.rename(columns={"OrderDate": "order_date", "OrderNumber": "order_number", "ProductKey": "product_id", "CustomerKey": "customer_id", "OrderQuantity": "order_quantity"})
    sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
    sales = sales.merge(products[["product_id", "product_name", "category_name", "subcategory_name", "product_price", "product_cost"]], on="product_id", how="left")
    sales["revenue"] = sales["order_quantity"] * sales["product_price"]
    sales["gross_profit"] = sales["order_quantity"] * (sales["product_price"] - sales["product_cost"])
    returns = returns.rename(columns={"ProductKey": "product_id", "ReturnQuantity": "returned_units"})
    return sales, customers, products, returns


def build_metrics():
    sales, customers, products, returns = load_data()
    monthly = sales.assign(month=sales["order_date"].dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(
        revenue=("revenue", "sum"), gross_profit=("gross_profit", "sum"), orders=("order_number", "nunique")
    )
    category = sales.groupby("category_name", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_quantity", "sum"), gross_profit=("gross_profit", "sum"))
    subcategory = sales.groupby("subcategory_name", as_index=False).agg(orders=("order_quantity", "sum"), revenue=("revenue", "sum")).sort_values("orders", ascending=False).head(15)
    product = sales.groupby(["product_id", "product_name", "category_name"], as_index=False).agg(units_sold=("order_quantity", "sum"), orders=("order_number", "nunique"), revenue=("revenue", "sum"), gross_profit=("gross_profit", "sum"))
    returned = returns.groupby("product_id", as_index=False)["returned_units"].sum()
    product = product.merge(returned, on="product_id", how="left").fillna({"returned_units": 0})
    product["return_rate_pct"] = product["returned_units"] / product["units_sold"].replace(0, pd.NA) * 100
    product["gross_margin_pct"] = product["gross_profit"] / product["revenue"].replace(0, pd.NA) * 100

    customer = sales.groupby("customer_id", as_index=False).agg(order_count=("order_number", "nunique"), units_purchased=("order_quantity", "sum"), lifetime_value=("revenue", "sum"), last_order_date=("order_date", "max"))
    customer = customer.merge(customers[["customer_id", "full_name", "gender", "annual_income", "occupation"]], on="customer_id", how="left")
    threshold = customer["lifetime_value"].quantile(0.75)
    customer["customer_segment"] = "Standard"
    customer.loc[customer["order_count"] >= 2, "customer_segment"] = "Repeat"
    customer.loc[customer["lifetime_value"] >= threshold, "customer_segment"] = "High Value"
    return {"sales": sales, "monthly": monthly, "category": category, "subcategory": subcategory, "product": product, "customer": customer, "products": products}


def card(title, value, color=COLORS["teal"]):
    return html.Div([html.Div(title, className="metric-title"), html.Div(value, className="metric-value", style={"color": color})], className="metric-card")


def chart(fig, title):
    fig.update_layout(title=title, template="plotly_white", margin={"l": 30, "r": 20, "t": 45, "b": 30}, height=330)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def table(frame, columns, title):
    return html.Div([html.H3(title), dash_table.DataTable(data=frame[columns].round(2).to_dict("records"), columns=[{"name": c.replace("_", " ").title(), "id": c} for c in columns], page_size=12, style_table={"overflowX": "auto"}, style_header={"backgroundColor": COLORS["navy"], "color": "white", "fontWeight": "bold"}, style_cell={"padding": "8px", "textAlign": "left"})], className="table-card")


def build_app():
    m = build_metrics()
    monthly, category, subcategory, product, customer, products = m["monthly"], m["category"], m["subcategory"], m["product"], m["customer"], m["products"]
    top_products = product.sort_values("gross_profit", ascending=False).head(20)
    top_customers = customer.sort_values("lifetime_value", ascending=False).head(50)
    segment_counts = customer["customer_segment"].value_counts()

    executive = html.Div([
        html.H1("Adventure Works Executive Summary"),
        html.Div([card("Total Revenue", f"${monthly.revenue.sum()/1e6:.2f}M"), card("Total Orders", f"{monthly.orders.sum():,.0f}"), card("Units Sold", f"{m['sales'].order_quantity.sum():,.0f}"), card("Gross Profit", f"${monthly.gross_profit.sum()/1e6:.2f}M")], className="metrics-row"),
        html.Div([chart(px.area(monthly, x="month", y="revenue", color_discrete_sequence=[COLORS["teal"]]), "Monthly Revenue"), chart(px.bar(category.sort_values("revenue", ascending=False), x="category_name", y="revenue", color="category_name"), "Revenue by Category")], className="chart-row"),
        html.Div([chart(px.bar(subcategory.sort_values("orders"), x="orders", y="subcategory_name", orientation="h", color_discrete_sequence=[COLORS["teal"]]), "Total Orders by Subcategory"), chart(px.bar(product.sort_values("return_rate_pct", ascending=False).head(15), x="return_rate_pct", y="product_name", orientation="h", color_discrete_sequence=[COLORS["red"]]), "Return Rate Hotspots")], className="chart-row"),
        table(top_products, ["product_name", "orders", "revenue", "gross_profit", "return_rate_pct"], "Top Product Detail"),
    ])

    customer_page = html.Div([
        html.H1("Adventure Works Customer Insights"),
        html.Div([card("Total Customers", f"{len(customer):,.0f}"), card("High Value", f"{segment_counts.get('High Value', 0):,.0f}", COLORS["gold"]), card("Repeat", f"{segment_counts.get('Repeat', 0):,.0f}"), card("Standard", f"{segment_counts.get('Standard', 0):,.0f}", COLORS["navy"])], className="metrics-row"),
        html.Div([chart(px.pie(customer, names="gender", values="order_count", hole=0.45), "Orders by Gender"), chart(px.pie(customer.assign(income_band=pd.cut(customer.annual_income, [-1, 50000, 100000, float("inf")], labels=["Low", "Average", "High"])), names="income_band", values="order_count", hole=0.45), "Orders by Income Band"), chart(px.pie(customer, names="occupation", values="order_count", hole=0.45), "Orders by Occupation")], className="chart-row"),
        html.Div([chart(px.line(monthly, x="month", y=["orders", "revenue"], title="Orders and Revenue by Month"), "Orders and Revenue by Month")], className="chart-row"),
        table(top_customers, ["full_name", "customer_segment", "order_count", "lifetime_value", "last_order_date"], "Top Customers"),
    ])

    product_page = html.Div([
        html.H1("Adventure Works Product Details"),
        html.Div([card("Total Products", f"{len(products):,.0f}"), card("Product Revenue", f"${product.revenue.sum()/1e6:.2f}M"), card("Product Gross Profit", f"${product.gross_profit.sum()/1e6:.2f}M"), card("Average Margin", f"{product.gross_margin_pct.mean():.1f}%", COLORS["gold"])], className="metrics-row"),
        html.Div([chart(px.bar(category.sort_values("revenue"), x="revenue", y="category_name", orientation="h", color_discrete_sequence=[COLORS["teal"]]), "Category Revenue"), chart(px.bar(top_products.sort_values("gross_profit"), x="gross_profit", y="product_name", orientation="h", color_discrete_sequence=[COLORS["teal"]]), "Top Products by Gross Profit")], className="chart-row"),
        html.Div([chart(px.line(monthly, x="month", y="gross_profit", color_discrete_sequence=[COLORS["teal"]]), "Monthly Gross Profit"), chart(px.bar(product.sort_values("return_rate_pct", ascending=False).head(15), x="return_rate_pct", y="product_name", orientation="h", color_discrete_sequence=[COLORS["red"]]), "Product Return Rate")], className="chart-row"),
        table(product.sort_values("gross_profit", ascending=False).head(100), ["product_name", "category_name", "units_sold", "revenue", "gross_profit", "gross_margin_pct"], "Product Profitability Detail"),
    ])

    app = Dash(__name__, title="Adventure Works Dashboard")
    app.layout = html.Div([dcc.Tabs([dcc.Tab(label="Executive Summary", children=executive), dcc.Tab(label="Customer Insights", children=customer_page), dcc.Tab(label="Product Details", children=product_page)], colors={"border": "white", "primary": COLORS["teal"], "background": "#f5f7f8"})], className="app-shell")
    return app


app = build_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", "8050")))
