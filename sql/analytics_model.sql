-- =========================================
-- ANALYTICS MODEL
-- Schema + Dimensions + Fact
-- =========================================

-- -------------------------
-- Schema
-- -------------------------
-- =====================================================
-- DIMENSIÓN: ZIP CODES
-- Grain: 1 row = 1 zip code prefix
-- =====================================================

CREATE SCHEMA IF NOT EXISTS analytics;

DROP VIEW IF EXISTS analytics.dim_zip_codes CASCADE;

CREATE OR REPLACE VIEW analytics.dim_zip_codes AS
SELECT
    geolocation_zip_code_prefix                          AS zip_code_prefix,
    ROUND(AVG(geolocation_lat)::numeric, 6)             AS avg_lat,
    ROUND(AVG(geolocation_lng)::numeric, 6)             AS avg_lng,
    MODE() WITHIN GROUP (ORDER BY geolocation_city)     AS city,
    MODE() WITHIN GROUP (ORDER BY geolocation_state)    AS state,
    COUNT(*)                                            AS total_locations
FROM geolocation_clean
GROUP BY geolocation_zip_code_prefix;

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
-- Dimension: Payment
-- Grain: 1 row = 1 order
-- -------------------------
CREATE OR REPLACE VIEW analytics.dim_payment AS
SELECT
    order_id,
    STRING_AGG(DISTINCT payment_type, ', ') AS payment_type,
    MAX(payment_installments)               AS payment_installments
FROM payments_clean
GROUP BY order_id;

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
