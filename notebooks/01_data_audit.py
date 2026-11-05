
import pandas as pd
from pathlib import Path

# ------------------------------------------------
# 1. DEFINE PROJECT PATHS
# ------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------
# 2. DEFINE DATASET FILES
# ------------------------------------------------

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

datasets = {}
audit_results = []
missing_results = []

# ------------------------------------------------
# 3. LOAD AND AUDIT DATASETS
# ------------------------------------------------

for table_name, filename in files.items():

    file_path = RAW_DIR / filename

    print("\n" + "=" * 65)
    print("TABLE:", table_name.upper())
    print("=" * 65)

    if not file_path.exists():
        print("FILE NOT FOUND:", file_path)
        continue

    df = pd.read_csv(file_path, low_memory=False)

    datasets[table_name] = df

    rows, columns = df.shape

    duplicate_count = int(df.duplicated().sum())

    missing_count = int(df.isnull().sum().sum())

    print("Rows:", rows)
    print("Columns:", columns)
    print("Duplicate rows:", duplicate_count)
    print("Total missing values:", missing_count)

    print("\nCOLUMN INFORMATION:")
    print(df.dtypes)

    print("\nMISSING VALUES BY COLUMN:")

    missing = df.isnull().sum()

    missing = missing[missing > 0]

    print(missing if not missing.empty else "No missing values")

    # Dataset-level summary

    audit_results.append({
        "table": table_name,
        "rows": rows,
        "columns": columns,
        "duplicate_rows": duplicate_count,
        "missing_values": missing_count
    })

    # Column-level missing-value summary

    for column in df.columns:

        missing_results.append({
            "table": table_name,
            "column": column,
            "missing_count": int(df[column].isnull().sum()),
            "missing_percentage": round(
                df[column].isnull().mean() * 100, 2
            )
        })

# ------------------------------------------------
# 4. SAVE AUDIT REPORTS
# ------------------------------------------------

audit_df = pd.DataFrame(audit_results)

missing_df = pd.DataFrame(missing_results)

audit_df.to_csv(
    REPORT_DIR / "dataset_audit_summary.csv",
    index=False
)

missing_df.to_csv(
    REPORT_DIR / "missing_values_report.csv",
    index=False
)

print("\n" + "=" * 65)
print("FINAL DATA AUDIT SUMMARY")
print("=" * 65)

print(audit_df.to_string(index=False))

print("\nAUDIT COMPLETED SUCCESSFULLY!")
print("Reports saved inside:", REPORT_DIR)
