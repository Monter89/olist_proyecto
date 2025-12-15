-- =========================================
-- ANALYTICS MODEL
-- Schema + Dimensions + Fact
-- =========================================

-- -------------------------
-- Schema
-- -------------------------
CREATE SCHEMA IF NOT EXISTS analytics;

-- -------------------------
-- Dimension: Time
-- -------------------------
CREATE OR REPLACE VIEW analytics.dim_time AS
SELECT DISTINCT
    DATE(o.order_purchase_timestamp)                 AS date,
    EXTRACT(YEAR FROM o.order_purchase_timestamp)    AS year,
    EXTRACT(MONTH FROM o.order_purchase_timestamp)   AS month,
    EXTRACT(DAY FROM o.order_purchase_timestamp)     AS day,
    EXTRACT(QUARTER FROM o.order_purchase_timestamp) AS quarter,
    TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')   AS year_month
FROM orders_clean o
WHERE o.order_purchase_timestamp IS NOT NULL;

-- -------------------------
-- Dimension: Customer
-- -------------------------
CREATE OR REPLACE VIEW analytics.dim_customer AS
SELECT
    customer_id,
    customer_city,
    customer_state,
    customer_zip_code_prefix
FROM customers_clean;

-- -------------------------
-- Dimension: Product
-- -------------------------
CREATE OR REPLACE VIEW analytics.dim_product AS
SELECT
    p.product_id,
    p.product_category_name,
    ct.product_category_name_english,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM products_clean p
LEFT JOIN categories_clean ct
  ON p.product_category_name = ct.product_category_name;

-- -------------------------
-- Dimension: Seller
-- -------------------------
CREATE OR REPLACE VIEW analytics.dim_seller AS
SELECT
    seller_id,
    seller_city,
    seller_state,
    seller_zip_code_prefix
FROM sellers_clean;

-- -------------------------
-- Dimension: Order
-- -------------------------
CREATE OR REPLACE VIEW analytics.dim_order AS
SELECT
    order_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
FROM orders_clean;

-- -------------------------
-- Fact: Order Items
-- Grain: 1 row = 1 item sold
-- -------------------------
CREATE OR REPLACE VIEW analytics.fact_order_items AS
SELECT
    -- Keys
    oi.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,

    -- Time
    DATE(o.order_purchase_timestamp) AS purchase_date,

    -- Measures
    oi.price,
    oi.freight_value,
    (oi.price + COALESCE(oi.freight_value, 0)) AS total_item_value,

    -- Attributes
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date
FROM order_items_clean oi
JOIN orders_clean o
  ON oi.order_id = o.order_id;
