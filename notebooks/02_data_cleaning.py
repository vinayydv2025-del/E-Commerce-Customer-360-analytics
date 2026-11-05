
import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# 1. PROJECT PATHS
# =====================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
REPORT_DIR = PROJECT_DIR / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# 2. LOAD ALL DATASETS
# =====================================================

files = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

data = {}

for name, filename in files.items():

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")

    data[name] = pd.read_csv(path, low_memory=False)

    print(f"Loaded {name}: {data[name].shape}")


# =====================================================
# 3. REMOVE EXACT DUPLICATE ROWS
# =====================================================

duplicate_report = []

for name, df in data.items():

    before = len(df)

    data[name] = df.drop_duplicates().copy()

    after = len(data[name])

    duplicate_report.append({
        "table": name,
        "duplicates_removed": before - after
    })

duplicate_df = pd.DataFrame(duplicate_report)

duplicate_df.to_csv(
    REPORT_DIR / "duplicate_removal_report.csv",
    index=False
)


# =====================================================
# 4. STANDARDIZE TEXT COLUMNS
# =====================================================

for name, df in data.items():

    for column in df.select_dtypes(include="object").columns:

        df[column] = df[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )


# =====================================================
# 5. CONVERT DATE COLUMNS
# =====================================================

date_columns = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp"
    ]
}

date_report = []

for table, columns in date_columns.items():

    df = data[table]

    for column in columns:

        original_missing = df[column].isna().sum()

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        newly_invalid = (
            df[column].isna().sum() - original_missing
        )

        date_report.append({
            "table": table,
            "column": column,
            "new_invalid_dates": int(newly_invalid)
        })


# =====================================================
# 6. CONVERT NUMERIC COLUMNS
# =====================================================

numeric_columns = {
    "order_items": ["price", "freight_value"],
    "payments": ["payment_sequential", "payment_installments",
                 "payment_value"],
    "reviews": ["review_score"],
    "products": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ],
    "geolocation": [
        "geolocation_lat",
        "geolocation_lng"
    ]
}

numeric_report = []

for table, columns in numeric_columns.items():

    df = data[table]

    for column in columns:

        original_missing = df[column].isna().sum()

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        newly_invalid = (
            df[column].isna().sum() - original_missing
        )

        numeric_report.append({
            "table": table,
            "column": column,
            "new_invalid_values": int(newly_invalid)
        })


# =====================================================
# 7. BUSINESS RULE VALIDATION
# =====================================================

items = data["order_items"]
payments = data["payments"]
reviews = data["reviews"]
geo = data["geolocation"]
orders = data["orders"]

# Negative price or freight

items["invalid_price_flag"] = items["price"] < 0

items["invalid_freight_flag"] = (
    items["freight_value"] < 0
)

# Invalid payment amounts

payments["invalid_payment_flag"] = (
    payments["payment_value"] < 0
)

payments["invalid_installment_flag"] = (
    payments["payment_installments"] < 0
)

# Review scores must be between 1 and 5

reviews["invalid_review_score_flag"] = (
    ~reviews["review_score"].between(1, 5)
    & reviews["review_score"].notna()
)

# Geographic coordinate validation

geo["invalid_latitude_flag"] = (
    ~geo["geolocation_lat"].between(-90, 90)
    & geo["geolocation_lat"].notna()
)

geo["invalid_longitude_flag"] = (
    ~geo["geolocation_lng"].between(-180, 180)
    & geo["geolocation_lng"].notna()
)

# Delivery date validation

orders["delivery_before_purchase_flag"] = (
    orders["order_delivered_customer_date"]
    < orders["order_purchase_timestamp"]
)

orders["delivery_before_purchase_flag"] = (
    orders["delivery_before_purchase_flag"].fillna(False)
)

# Delivered status but missing delivery date

orders["delivered_missing_date_flag"] = (
    (orders["order_status"] == "delivered")
    & orders["order_delivered_customer_date"].isna()
)


# =====================================================
# 8. PRIMARY KEY VALIDATION
# =====================================================

key_checks = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "category_translation": ["product_category_name"],
    "order_items": ["order_id", "order_item_id"]
}

key_report = []

for table, columns in key_checks.items():

    df = data[table]

    duplicate_count = int(
        df.duplicated(subset=columns).sum()
    )

    null_count = int(
        df[columns].isna().any(axis=1).sum()
    )

    key_report.append({
        "table": table,
        "key_columns": ", ".join(columns),
        "duplicate_key_rows": duplicate_count,
        "null_key_rows": null_count
    })


# =====================================================
# 9. REFERENTIAL INTEGRITY VALIDATION
# =====================================================

customers = data["customers"]
orders = data["orders"]
order_items = data["order_items"]
products = data["products"]
sellers = data["sellers"]
payments = data["payments"]
reviews = data["reviews"]

relationships = [
    (
        "orders_customer",
        orders,
        "customer_id",
        customers,
        "customer_id"
    ),
    (
        "items_order",
        order_items,
        "order_id",
        orders,
        "order_id"
    ),
    (
        "items_product",
        order_items,
        "product_id",
        products,
        "product_id"
    ),
    (
        "items_seller",
        order_items,
        "seller_id",
        sellers,
        "seller_id"
    ),
    (
        "payments_order",
        payments,
        "order_id",
        orders,
        "order_id"
    ),
    (
        "reviews_order",
        reviews,
        "order_id",
        orders,
        "order_id"
    )
]

relationship_report = []

for name, child, child_col, parent, parent_col in relationships:

    unmatched = ~child[child_col].isin(
        parent[parent_col]
    )

    relationship_report.append({
        "relationship": name,
        "unmatched_rows": int(unmatched.sum())
    })


# =====================================================
# 10. CREATE DATA QUALITY REPORT
# =====================================================

quality_report = []

for name, df in data.items():

    quality_report.append({
        "table": name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "exact_duplicate_rows": int(df.duplicated().sum())
    })


# =====================================================
# 11. SAVE REPORTS
# =====================================================

pd.DataFrame(date_report).to_csv(
    REPORT_DIR / "date_validation_report.csv",
    index=False
)

pd.DataFrame(numeric_report).to_csv(
    REPORT_DIR / "numeric_validation_report.csv",
    index=False
)

pd.DataFrame(key_report).to_csv(
    REPORT_DIR / "primary_key_validation.csv",
    index=False
)

pd.DataFrame(relationship_report).to_csv(
    REPORT_DIR / "referential_integrity_report.csv",
    index=False
)

pd.DataFrame(quality_report).to_csv(
    REPORT_DIR / "data_quality_report.csv",
    index=False
)


# =====================================================
# 12. EXPORT CLEANED DATASETS
# =====================================================

for name, df in data.items():

    output_path = PROCESSED_DIR / f"{name}_cleaned.csv"

    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path.name}")


# =====================================================
# 13. FINAL SUMMARY
# =====================================================

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED")
print("=" * 60)

print("\nDuplicate removal:")
print(duplicate_df.to_string(index=False))

print("\nPrimary key validation:")
print(pd.DataFrame(key_report).to_string(index=False))

print("\nReferential integrity:")
print(pd.DataFrame(relationship_report).to_string(index=False))

print("\nAll reports saved in:", REPORT_DIR)
print("Cleaned datasets saved in:", PROCESSED_DIR)
