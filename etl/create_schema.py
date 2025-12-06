import sqlalchemy
from sqlalchemy import create_engine, text

# ============================================
# DATABASE CONNECTION
# ============================================

engine = create_engine(
    "postgresql://olist_user:olist_pass@localhost:5433/olist_analytics"
)

print("🚀 Connected to PostgreSQL!")

# ============================================
# SCHEMA CREATION QUERIES
# ============================================

schema_sql = """

-- Drop existing tables if needed (optional)
DROP TABLE IF EXISTS fact_order_items CASCADE;
DROP TABLE IF EXISTS dim_order CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_seller CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- DIM CUSTOMER
CREATE TABLE dim_customer (
    customer_id VARCHAR PRIMARY KEY,
    customer_unique_id VARCHAR,
    customer_zip_code_prefix INT,
    customer_city VARCHAR,
    customer_state VARCHAR
);

-- DIM PRODUCT
CREATE TABLE dim_product (
    product_id VARCHAR PRIMARY KEY,
    product_category_name VARCHAR,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- DIM SELLER
CREATE TABLE dim_seller (
    seller_id VARCHAR PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR,
    seller_state VARCHAR
);

-- DIM DATE
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    weekday INT
);

-- DIM ORDER
CREATE TABLE dim_order (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR,
    order_status VARCHAR,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);


-- FACT ORDER ITEMS
CREATE TABLE fact_order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR,
    product_id VARCHAR,
    seller_id VARCHAR,
    shipping_limit_date TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC
);

"""

# ============================================
# EXECUTE SCHEMA CREATION
# ============================================

with engine.connect() as conn:
    conn.execute(text(schema_sql))
    conn.commit()

print("🎉 Dimensional schema created successfully!")
