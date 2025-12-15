import pandas as pd
import numpy as np
from pathlib import Path
from calendar import monthrange

# -----------------------
# Paths
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"


# -----------------------
# Load function
# -----------------------
def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    return pd.read_csv(path)


# -----------------------
# Helpers
# -----------------------
def fix_invalid_ddmmyyyy(value):
    """
    Corrige fechas DD/MM/YYYY inválidas.
    - Mes > 12 => enero del año siguiente
    - Día fuera de rango => último día del mes
    """
    try:
        s = str(value).strip()
        if not s or s.lower() in {"nan", "nat", "none"}:
            return pd.NaT

        day, month, year = map(int, s.split("/"))

        if month > 12:
            month = 1
            year += 1

        max_day = monthrange(year, month)[1]
        if day > max_day:
            day = max_day

        return pd.Timestamp(year, month, day)

    except Exception:
        return pd.NaT


# -----------------------
# Customers
# -----------------------
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="customer_id")

    df["customer_city"] = (
        df["customer_city"]
        .astype(str)
        .str.encode("latin1", errors="ignore")
        .str.decode("utf-8", errors="ignore")
        .str.lower()
        .str.strip()
    )

    df["customer_zip_code_prefix"] = pd.to_numeric(
        df["customer_zip_code_prefix"], errors="coerce"
    )

    df.loc[
        (df["customer_zip_code_prefix"] <= 0) |
        (df["customer_zip_code_prefix"] > 99999),
        "customer_zip_code_prefix"
    ] = np.nan

    return df


# -----------------------
# Orders
# -----------------------
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="order_id")

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df.loc[
        df["order_approved_at"] < df["order_purchase_timestamp"],
        "order_approved_at"
    ] = np.nan

    df.loc[
        df["order_delivered_carrier_date"] < df["order_approved_at"],
        "order_delivered_carrier_date"
    ] = np.nan

    df.loc[
        df["order_delivered_customer_date"] < df["order_delivered_carrier_date"],
        "order_delivered_customer_date"
    ] = np.nan

    return df


# -----------------------
# Order Items
# -----------------------
def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["order_id", "order_item_id"])

    # FIX: corrección robusta de fechas inválidas
    df["shipping_limit_date"] = df["shipping_limit_date"].apply(fix_invalid_ddmmyyyy)

    for col in ["price", "freight_value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["price"] > 0]
    df.loc[df["freight_value"] < 0, "freight_value"] = np.nan

    return df


# -----------------------
# Payments
# -----------------------
def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["order_id", "payment_sequential"])

    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")
    df["payment_installments"] = pd.to_numeric(
        df["payment_installments"], errors="coerce"
    )

    df = df[df["payment_value"] > 0]
    df.loc[df["payment_installments"] <= 0, "payment_installments"] = np.nan

    df["payment_type"] = (
        df["payment_type"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    return df


# -----------------------
# Products
# -----------------------
def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="product_id")

    numeric_cols = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[df[col] <= 0, col] = np.nan

    df["product_category_name"] = (
        df["product_category_name"]
        .astype(str)
        .str.encode("latin1", errors="ignore")
        .str.decode("utf-8", errors="ignore")
        .str.lower()
        .str.strip()
    )

    df.loc[df["product_category_name"] == "", "product_category_name"] = np.nan

    return df


# -----------------------
# Reviews
# -----------------------
def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="review_id")

    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")
    df = df[df["review_score"].between(1, 5)]

    for col in ["review_creation_date", "review_answer_timestamp"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df.loc[
        df["review_answer_timestamp"] < df["review_creation_date"],
        "review_answer_timestamp"
    ] = np.nan

    for col in ["review_comment_title", "review_comment_message"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.encode("latin1", errors="ignore")
            .str.decode("utf-8", errors="ignore")
            .str.strip()
        )
        df.loc[df[col] == "", col] = np.nan

    return df


# -----------------------
# Sellers
# -----------------------
def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="seller_id")

    df["seller_city"] = (
        df["seller_city"]
        .astype(str)
        .str.encode("latin1", errors="ignore")
        .str.decode("utf-8", errors="ignore")
        .str.lower()
        .str.strip()
    )

    df.loc[df["seller_city"] == "", "seller_city"] = np.nan

    df["seller_zip_code_prefix"] = pd.to_numeric(
        df["seller_zip_code_prefix"], errors="coerce"
    )

    df.loc[
        (df["seller_zip_code_prefix"] <= 0) |
        (df["seller_zip_code_prefix"] > 99999),
        "seller_zip_code_prefix"
    ] = np.nan

    df["seller_state"] = (
        df["seller_state"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df.loc[df["seller_state"] == "", "seller_state"] = np.nan

    return df


# -----------------------
# Geolocation
# -----------------------
def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()

    df["geolocation_lat"] = pd.to_numeric(df["geolocation_lat"], errors="coerce")
    df["geolocation_lng"] = pd.to_numeric(df["geolocation_lng"], errors="coerce")

    df = df[
        df["geolocation_lat"].between(-90, 90) &
        df["geolocation_lng"].between(-180, 180)
    ]

    df["geolocation_city"] = (
        df["geolocation_city"]
        .astype(str)
        .str.encode("latin1", errors="ignore")
        .str.decode("utf-8", errors="ignore")
        .str.lower()
        .str.strip()
    )

    df.loc[df["geolocation_city"] == "", "geolocation_city"] = np.nan

    df["geolocation_state"] = (
        df["geolocation_state"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df.loc[df["geolocation_state"] == "", "geolocation_state"] = np.nan

    df["geolocation_zip_code_prefix"] = pd.to_numeric(
        df["geolocation_zip_code_prefix"], errors="coerce"
    )

    df.loc[
        (df["geolocation_zip_code_prefix"] <= 0) |
        (df["geolocation_zip_code_prefix"] > 99999),
        "geolocation_zip_code_prefix"
    ] = np.nan

    return df


# -----------------------
# Category Translation
# -----------------------
def clean_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="product_category_name")

    for col in ["product_category_name", "product_category_name_english"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.encode("latin1", errors="ignore")
            .str.decode("utf-8", errors="ignore")
            .str.lower()
            .str.strip()
        )

    df.loc[df["product_category_name"] == "", "product_category_name"] = np.nan
    df.loc[
        df["product_category_name_english"].isna() |
        (df["product_category_name_english"] == ""),
        "product_category_name_english"
    ] = "unknown"

    return df


# -----------------------
# Main
# -----------------------
def main():
    print("Starting CLEAN pipeline")

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    pipelines = [
        ("customers", "olist_customers_dataset_dirty.csv", clean_customers),
        ("orders", "olist_orders_dataset_dirty.csv", clean_orders),
        ("order_items", "olist_order_items_dataset_dirty.csv", clean_order_items),
        ("payments", "olist_order_payments_dataset_dirty.csv", clean_payments),
        ("products", "olist_products_dataset_dirty.csv", clean_products),
        ("reviews", "olist_order_reviews_dataset_dirty.csv", clean_reviews),
        ("sellers", "olist_sellers_dataset_dirty.csv", clean_sellers),
        ("geolocation", "olist_geolocation_dataset_dirty.csv", clean_geolocation),
        ("categories", "product_category_name_translation_dirty.csv", clean_category_translation),
    ]

    for name, file, func in pipelines:
        df = load_csv(file)
        print(f"{name} loaded:", df.shape)

        df_clean = func(df)
        print(f"{name} cleaned:", df_clean.shape)

        df_clean.to_csv(
            CLEAN_DIR / f"{name}_clean.csv",
            index=False,
            date_format="%Y-%m-%d %H:%M:%S"
        )
        print(f"{name} CLEAN saved")

    print("CLEAN pipeline finished")


if __name__ == "__main__":
    main()
