import sqlalchemy
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://olist_user:olist_pass@localhost:5433/olist_analytics")
print("🚀 Connected to PostgreSQL!")

def run(sql):
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

# ============================================
# DROP OLD TABLES
# ============================================

print("🗑️ Dropping old star schema...")

run("DROP TABLE IF EXISTS fact_order_items CASCADE;")
run("DROP TABLE IF EXISTS dim_order CASCADE;")
run("DROP TABLE IF EXISTS dim_customer CASCADE;")
run("DROP TABLE IF EXISTS dim_product CASCADE;")
run("DROP TABLE IF EXISTS dim_seller CASCADE;")
run("DROP TABLE IF EXISTS dim_date CASCADE;")

# ============================================
# CREATE DIMENSIONS
# ============================================

print("🏗 Creating dimensions...")

run("""
CREATE TABLE dim_customer (
    customer_id VARCHAR PRIMARY KEY,
    customer_unique_id VARCHAR,
    customer_zip_code_prefix INT,
    customer_city VARCHAR,
    customer_state VARCHAR
);
""")

run("""
CREATE TABLE dim_product (
    product_id VARCHAR PRIMARY KEY,
    product_category_name VARCHAR,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);
""")

run("""
CREATE TABLE dim_seller (
    seller_id VARCHAR PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR,
    seller_state VARCHAR
);
""")

run("""
CREATE TABLE dim_order (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR,
    order_status VARCHAR,
    purchase_timestamp TIMESTAMP,
    approved_at TIMESTAMP,
    delivered_carrier_date TIMESTAMP,
    delivered_customer_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP
);
""")

run("""
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    weekday INT
);
""")

run("""
CREATE TABLE fact_order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR,
    product_id VARCHAR,
    seller_id VARCHAR,
    shipping_limit_date TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC
);
""")

print("✨ Schema created!")

# ============================================
# LOAD DIMENSIONS
# ============================================

print("📥 Loading data...")

run("""
INSERT INTO dim_customer
SELECT customer_id, customer_unique_id, customer_zip_code_prefix,
       customer_city, customer_state
FROM customers;
""")

run("""
INSERT INTO dim_product
SELECT product_id, product_category_name, product_weight_g,
       product_length_cm, product_height_cm, product_width_cm
FROM products;
""")

run("""
INSERT INTO dim_seller
SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state
FROM sellers;
""")

run("""
INSERT INTO dim_order
SELECT
    order_id,
    customer_id,
    order_status,
    purchase_timestamp,
    approved_at,
    delivered_carrier_date,
    delivered_customer_date,
    estimated_delivery_date
FROM orders;
""")

# ============================================
# AUTO GENERATE dim_date
# ============================================

print("📅 Generating dim_date...")

run("""
INSERT INTO dim_date (date_id, year, month, day, weekday)
SELECT
    d::date AS date_id,
    EXTRACT(YEAR FROM d)::int AS year,
    EXTRACT(MONTH FROM d)::int AS month,
    EXTRACT(DAY FROM d)::int AS day,
    EXTRACT(DOW FROM d)::int AS weekday
FROM generate_series(
    (SELECT MIN(purchase_timestamp)::date FROM orders),
    (SELECT MAX(estimated_delivery_date)::date FROM orders),
    '1 day'
) AS d;
""")

print("📅 dim_date loaded successfully!")

# ============================================
# FACT TABLE
# ============================================

run("""
INSERT INTO fact_order_items (
    order_id, product_id, seller_id,
    shipping_limit_date, price, freight_value
)
SELECT
    order_id, product_id, seller_id,
    shipping_limit_date, price, freight_value
FROM order_items;
""")

print("🎉 Star schema loaded successfully!")
