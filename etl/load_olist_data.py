import pandas as pd
from sqlalchemy import create_engine
import os

# ============================
# Paths and database settings
# ============================

BASE_DIR = r"C:\Users\gasto\Documents\BootcampDevlights\olist_proyecto"
data_dir = os.path.join(BASE_DIR, "data", "raw")

engine = create_engine(
    "postgresql://olist_user:olist_pass@localhost:5433/olist_analytics"
)

print("Database connection successful!")


# ============================
# Helper function
# ============================

def load_csv_to_table(csv_file, table_name, columns=None, rename_map=None):
    file_path = os.path.join(data_dir, csv_file)
    df = pd.read_csv(file_path, encoding="latin1")

    # FIX para remover BOM
    if df.columns[0].startswith("ï»¿"):
        df.rename(columns={df.columns[0]: df.columns[0].replace("ï»¿", "")}, inplace=True)

    # Renombrar columnas si se pasó rename_map
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # Seleccionar columnas
    if columns:
        df = df[columns]

    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"✔ Loaded table: {table_name}")


# ============================
# Load datasets
# ============================

load_csv_to_table(
    "product_category_name_translation.csv",
    "categories",
    ["product_category_name", "product_category_name_english"]
)

load_csv_to_table(
    "olist_customers_dataset.csv",
    "customers",
    [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]
)

load_csv_to_table("olist_geolocation_dataset.csv", "geolocation")

load_csv_to_table("olist_sellers_dataset.csv", "sellers")

load_csv_to_table("olist_products_dataset.csv", "products")

load_csv_to_table(
    "olist_orders_dataset.csv",
    "orders",
    [
        "order_id",
        "customer_id",
        "order_status",
        "purchase_timestamp",
        "approved_at",
        "delivered_carrier_date",
        "delivered_customer_date",
        "estimated_delivery_date",
    ],
    rename_map={
        "order_purchase_timestamp": "purchase_timestamp",
        "order_approved_at": "approved_at",
        "order_delivered_carrier_date": "delivered_carrier_date",
        "order_delivered_customer_date": "delivered_customer_date",
        "order_estimated_delivery_date": "estimated_delivery_date",
    }
)


load_csv_to_table("olist_order_items_dataset.csv", "order_items")

load_csv_to_table("olist_order_payments_dataset.csv", "payments")

load_csv_to_table("olist_order_reviews_dataset.csv", "reviews")


print("\n🎉 ETL completed successfully.")
