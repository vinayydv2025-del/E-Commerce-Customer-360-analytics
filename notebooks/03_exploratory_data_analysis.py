
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

REPORTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# 2. LOAD CLEANED DATASETS
# --------------------------------------------------

customers = pd.read_csv(PROCESSED_DIR / "customers_cleaned.csv")
orders = pd.read_csv(
    PROCESSED_DIR / "orders_cleaned.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)
order_items = pd.read_csv(PROCESSED_DIR / "order_items_cleaned.csv")
products = pd.read_csv(PROCESSED_DIR / "products_cleaned.csv")
reviews = pd.read_csv(PROCESSED_DIR / "reviews_cleaned.csv")
category_translation = pd.read_csv(
    PROCESSED_DIR / "category_translation_cleaned.csv"
)

print("All required datasets loaded successfully.")

# --------------------------------------------------
# 3. UNDERSTAND ORDER STATUS
# --------------------------------------------------

print("\nORDER STATUS DISTRIBUTION")
print(orders["order_status"].value_counts(dropna=False))

status_summary = (
    orders["order_status"]
    .value_counts(dropna=False)
    .rename_axis("order_status")
    .reset_index(name="order_count")
)

status_summary.to_csv(
    REPORTS_DIR / "order_status_summary.csv",
    index=False
)

plt.figure(figsize=(10, 5))
status_summary.plot(
    x="order_status",
    y="order_count",
    kind="bar",
    legend=False
)
plt.title("Order Status Distribution")
plt.xlabel("Order Status")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "01_order_status.png", dpi=300)
plt.close()

# --------------------------------------------------
# 4. PREPARE DELIVERED ORDERS
# --------------------------------------------------

delivered_orders = orders[
    orders["order_status"] == "delivered"
].copy()

print("\nTotal delivered orders:", len(delivered_orders))

# --------------------------------------------------
# 5. ORDER-LEVEL SALES ANALYSIS
# --------------------------------------------------

# Aggregate items before joining to orders.
# This prevents multiple items from multiplying order records.

order_sales = (
    order_items.groupby("order_id", as_index=False)
    .agg(
        item_revenue=("price", "sum"),
        freight_revenue=("freight_value", "sum"),
        item_count=("order_item_id", "count")
    )
)

order_sales["order_value_including_freight"] = (
    order_sales["item_revenue"] +
    order_sales["freight_revenue"]
)

sales_data = delivered_orders.merge(
    order_sales,
    on="order_id",
    how="inner"
)

total_revenue = sales_data["item_revenue"].sum()
total_freight = sales_data["freight_revenue"].sum()
total_orders = sales_data["order_id"].nunique()
average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

print("\nSALES OVERVIEW")
print("Delivered orders:", total_orders)
print("Item revenue:", round(total_revenue, 2))
print("Freight charges:", round(total_freight, 2))
print("Average item revenue per delivered order:", round(average_order_value, 2))

sales_summary = pd.DataFrame({
    "metric": [
        "Delivered Orders",
        "Item Revenue",
        "Freight Charges",
        "Average Item Revenue Per Order"
    ],
    "value": [
        total_orders,
        total_revenue,
        total_freight,
        average_order_value
    ]
})

sales_summary.to_csv(
    REPORTS_DIR / "sales_summary.csv",
    index=False
)

# --------------------------------------------------
# 6. MONTHLY REVENUE TREND
# --------------------------------------------------

sales_data["purchase_month"] = (
    sales_data["order_purchase_timestamp"].dt.to_period("M").astype(str)
)

monthly_sales = (
    sales_data.groupby("purchase_month", as_index=False)
    .agg(
        revenue=("item_revenue", "sum"),
        orders=("order_id", "nunique")
    )
)

monthly_sales.to_csv(
    REPORTS_DIR / "monthly_sales_trend.csv",
    index=False
)

plt.figure(figsize=(13, 5))
plt.plot(
    monthly_sales["purchase_month"],
    monthly_sales["revenue"],
    marker="o"
)
plt.title("Monthly Item Revenue — Delivered Orders")
plt.xlabel("Month")
plt.ylabel("Item Revenue")
plt.xticks(rotation=60)
plt.grid(True)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "02_monthly_revenue.png", dpi=300)
plt.close()

# --------------------------------------------------
# 7. PRODUCT CATEGORY ANALYSIS
# --------------------------------------------------

items_with_products = order_items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)

items_with_products = items_with_products.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

delivered_items = items_with_products.merge(
    delivered_orders[["order_id"]],
    on="order_id",
    how="inner"
)

delivered_items["category_name_english"] = (
    delivered_items["product_category_name_english"]
    .fillna(delivered_items["product_category_name"])
    .fillna("Unknown")
)

category_sales = (
    delivered_items.groupby("category_name_english", as_index=False)
    .agg(
        item_revenue=("price", "sum"),
        items_sold=("order_item_id", "count")
    )
    .sort_values("item_revenue", ascending=False)
)

category_sales.to_csv(
    REPORTS_DIR / "category_sales_analysis.csv",
    index=False
)

top_categories = category_sales.head(10)

plt.figure(figsize=(12, 6))
plt.barh(
    top_categories["category_name_english"],
    top_categories["item_revenue"]
)
plt.title("Top 10 Product Categories by Item Revenue")
plt.xlabel("Item Revenue")
plt.ylabel("Product Category")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(FIGURES_DIR / "03_top_categories.png", dpi=300)
plt.close()

# --------------------------------------------------
# 8. CUSTOMER REPEAT PURCHASE ANALYSIS
# --------------------------------------------------

customer_orders = delivered_orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id",
    how="left"
)

customer_purchase_counts = (
    customer_orders.groupby("customer_unique_id", as_index=False)
    .agg(delivered_orders=("order_id", "nunique"))
)

customer_purchase_counts["customer_type"] = (
    customer_purchase_counts["delivered_orders"]
    .apply(lambda count: "Repeat Customer" if count > 1 else "One-Time Customer")
)

repeat_summary = (
    customer_purchase_counts["customer_type"]
    .value_counts()
    .rename_axis("customer_type")
    .reset_index(name="customer_count")
)

repeat_summary.to_csv(
    REPORTS_DIR / "customer_repeat_purchase_summary.csv",
    index=False
)

print("\nCUSTOMER PURCHASE BEHAVIOUR")
print(repeat_summary)

plt.figure(figsize=(7, 5))
plt.bar(
    repeat_summary["customer_type"],
    repeat_summary["customer_count"]
)
plt.title("One-Time vs Repeat Customers")
plt.xlabel("Customer Type")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "04_repeat_customers.png", dpi=300)
plt.close()

# --------------------------------------------------
# 9. DELIVERY PERFORMANCE ANALYSIS
# --------------------------------------------------

delivery_data = delivered_orders.dropna(
    subset=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
).copy()

delivery_data["actual_delivery_days"] = (
    delivery_data["order_delivered_customer_date"] -
    delivery_data["order_purchase_timestamp"]
).dt.total_seconds() / 86400

delivery_data["delivery_delay_days"] = (
    delivery_data["order_delivered_customer_date"] -
    delivery_data["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

delivery_data["delivery_result"] = (
    delivery_data["delivery_delay_days"]
    .apply(lambda days: "Late" if days > 0 else "On Time or Early")
)

delivery_summary = (
    delivery_data.groupby("delivery_result", as_index=False)
    .agg(order_count=("order_id", "nunique"))
)

delivery_summary.to_csv(
    REPORTS_DIR / "delivery_performance_summary.csv",
    index=False
)

print("\nDELIVERY PERFORMANCE")
print("Average delivery time (days):",
      round(delivery_data["actual_delivery_days"].mean(), 2))
print(delivery_summary)

plt.figure(figsize=(7, 5))
plt.bar(
    delivery_summary["delivery_result"],
    delivery_summary["order_count"]
)
plt.title("Late vs On-Time/Early Deliveries")
plt.xlabel("Delivery Result")
plt.ylabel("Number of Orders")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "05_delivery_performance.png", dpi=300)
plt.close()

# --------------------------------------------------
# 10. REVIEW SCORE ANALYSIS
# --------------------------------------------------

review_summary = (
    reviews.groupby("review_score", as_index=False)
    .agg(review_count=("review_id", "count"))
    .sort_values("review_score")
)

review_summary.to_csv(
    REPORTS_DIR / "review_score_distribution.csv",
    index=False
)

plt.figure(figsize=(8, 5))
plt.bar(
    review_summary["review_score"].astype(str),
    review_summary["review_count"]
)
plt.title("Customer Review Score Distribution")
plt.xlabel("Review Score")
plt.ylabel("Number of Reviews")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "06_review_scores.png", dpi=300)
plt.close()

# --------------------------------------------------
# 11. DELIVERY DELAY VS REVIEW SCORE
# --------------------------------------------------

order_reviews = (
    reviews.groupby("order_id", as_index=False)
    .agg(average_review_score=("review_score", "mean"))
)

delivery_reviews = delivery_data.merge(
    order_reviews,
    on="order_id",
    how="inner"
)

delay_review_summary = (
    delivery_reviews.groupby("delivery_result", as_index=False)
    .agg(
        average_review_score=("average_review_score", "mean"),
        orders=("order_id", "nunique")
    )
)

delay_review_summary.to_csv(
    REPORTS_DIR / "delivery_vs_reviews.csv",
    index=False
)

print("\nDELIVERY VS CUSTOMER REVIEWS")
print(delay_review_summary)

# --------------------------------------------------
# 12. FINAL OUTPUT
# --------------------------------------------------

print("\n====================================")
print("EDA COMPLETED SUCCESSFULLY")
print("====================================")
print("Analysis tables saved in:", REPORTS_DIR)
print("Charts saved in:", FIGURES_DIR)
