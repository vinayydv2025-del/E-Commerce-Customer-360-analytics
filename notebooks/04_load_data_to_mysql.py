
import pandas as pd
from pathlib import Path
from getpass import getpass
from sqlalchemy import create_engine, URL, text

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# --------------------------------------------------
# 2. MYSQL CONNECTION DETAILS
# --------------------------------------------------

host = "localhost"
port = 3306
username = input("Enter MySQL username (usually root): ")
password = getpass("Enter MySQL password: ")

database = "ecommerce_customer_360"

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=username,
    password=password,
    host=host,
    port=port,
    database=database
)

engine = create_engine(connection_url)

# --------------------------------------------------
# 3. TEST MYSQL CONNECTION
# --------------------------------------------------

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        print("Connected to database:", result.scalar())

except Exception as error:
    print("MySQL connection failed:", error)
    engine.dispose()
    raise SystemExit

# --------------------------------------------------
# 4. DATASET MAPPING
# --------------------------------------------------

datasets = {
    "customers": "customers_cleaned.csv",
    "orders": "orders_cleaned.csv",
    "order_items": "order_items_cleaned.csv",
    "order_payments": "payments_cleaned.csv",
    "order_reviews": "reviews_cleaned.csv",
    "products": "products_cleaned.csv",
    "sellers": "sellers_cleaned.csv",
    "geolocation": "geolocation_cleaned.csv",
    "category_translation": "category_translation_cleaned.csv"
}

# --------------------------------------------------
# 5. LOAD CSV FILES INTO MYSQL
# --------------------------------------------------

try:
    for table_name, file_name in datasets.items():

        file_path = PROCESSED_DIR / file_name

        print(f"\nLoading {table_name}...")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(file_path)

        # Convert date columns
        if table_name == "orders":
            date_columns = [
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date"
            ]

            for column in date_columns:
                df[column] = pd.to_datetime(
                    df[column], errors="coerce"
                )

        elif table_name == "order_reviews":
            date_columns = [
                "review_creation_date",
                "review_answer_timestamp"
            ]

            for column in date_columns:
                df[column] = pd.to_datetime(
                    df[column], errors="coerce"
                )

        # Initial load: replace existing tables if rerun
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=2000
        )

        print(f"Successfully loaded {len(df):,} rows.")

    print("\nALL NINE DATASETS LOADED SUCCESSFULLY!")

except Exception as error:
    print("\nDATA LOADING FAILED:", error)

finally:
    engine.dispose()
