-- =====================================================
-- CLEAN TABLES (ALIGNED WITH CLEAN CSV FILES)
-- =====================================================

-- ------------------------
-- Categories (translation)
-- ------------------------
DROP TABLE IF EXISTS public.categories_clean CASCADE;

CREATE TABLE public.categories_clean (
    product_category_name TEXT NOT NULL,
    product_category_name_english TEXT NOT NULL
);

ALTER TABLE categories_clean
ADD CONSTRAINT pk_categories_clean
PRIMARY KEY (product_category_name);

-- ------------------------
-- Customers
-- ------------------------
DROP TABLE IF EXISTS public.customers_clean CASCADE;

CREATE TABLE public.customers_clean (
    customer_id TEXT NOT NULL,
    customer_unique_id TEXT,
    customer_zip_code_prefix BIGINT,
    customer_city TEXT,
    customer_state TEXT
);

ALTER TABLE customers_clean
ADD CONSTRAINT pk_customers_clean
PRIMARY KEY (customer_id);

-- ------------------------
-- Orders
-- ------------------------
DROP TABLE IF EXISTS public.orders_clean CASCADE;

CREATE TABLE public.orders_clean (
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

ALTER TABLE orders_clean
ADD CONSTRAINT pk_orders_clean
PRIMARY KEY (order_id);

ALTER TABLE orders_clean
ADD CONSTRAINT fk_orders_customers
FOREIGN KEY (customer_id)
REFERENCES customers_clean(customer_id)
NOT VALID;

-- ------------------------
-- Products
-- ------------------------
DROP TABLE IF EXISTS public.products_clean CASCADE;

CREATE TABLE public.products_clean (
    product_id TEXT NOT NULL,
    product_category_name TEXT,
    product_name_length NUMERIC,
    product_description_length NUMERIC,
    product_photos_qty NUMERIC,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC
);

ALTER TABLE products_clean
ADD CONSTRAINT pk_products_clean
PRIMARY KEY (product_id);

ALTER TABLE products_clean
ADD CONSTRAINT fk_products_category
FOREIGN KEY (product_category_name)
REFERENCES categories_clean(product_category_name)
NOT VALID;

-- ------------------------
-- Sellers
-- ------------------------
DROP TABLE IF EXISTS public.sellers_clean CASCADE;

CREATE TABLE public.sellers_clean (
    seller_id TEXT NOT NULL,
    seller_zip_code_prefix BIGINT,
    seller_city TEXT,
    seller_state TEXT
);

ALTER TABLE sellers_clean
ADD CONSTRAINT pk_sellers_clean
PRIMARY KEY (seller_id);

-- ------------------------
-- Order Items
-- ------------------------
DROP TABLE IF EXISTS public.order_items_clean CASCADE;

CREATE TABLE public.order_items_clean (
    order_id TEXT NOT NULL,
    order_item_id NUMERIC NOT NULL,
    product_id TEXT NOT NULL,
    seller_id TEXT,
    shipping_limit_date TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC
);

ALTER TABLE order_items_clean
ADD CONSTRAINT pk_order_items_clean
PRIMARY KEY (order_id, order_item_id);

ALTER TABLE order_items_clean
ADD CONSTRAINT fk_items_orders
FOREIGN KEY (order_id)
REFERENCES orders_clean(order_id)
NOT VALID;

ALTER TABLE order_items_clean
ADD CONSTRAINT fk_items_products
FOREIGN KEY (product_id)
REFERENCES products_clean(product_id)
NOT VALID;

ALTER TABLE order_items_clean
ADD CONSTRAINT fk_items_sellers
FOREIGN KEY (seller_id)
REFERENCES sellers_clean(seller_id)
NOT VALID;

-- ------------------------
-- Payments
-- ------------------------
DROP TABLE IF EXISTS public.payments_clean CASCADE;

CREATE TABLE public.payments_clean (
    order_id TEXT NOT NULL,
    payment_sequential NUMERIC,
    payment_type TEXT,
    payment_installments NUMERIC,
    payment_value NUMERIC
);

ALTER TABLE payments_clean
ADD CONSTRAINT pk_payments_clean
PRIMARY KEY (order_id, payment_sequential);

ALTER TABLE payments_clean
ADD CONSTRAINT fk_payments_orders
FOREIGN KEY (order_id)
REFERENCES orders_clean(order_id)
NOT VALID;

-- ------------------------
-- Reviews
-- ------------------------
DROP TABLE IF EXISTS public.reviews_clean CASCADE;

CREATE TABLE public.reviews_clean (
    review_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    review_score NUMERIC NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

ALTER TABLE reviews_clean
ADD CONSTRAINT pk_reviews_clean
PRIMARY KEY (review_id);

ALTER TABLE reviews_clean
ADD CONSTRAINT fk_reviews_orders
FOREIGN KEY (order_id)
REFERENCES orders_clean(order_id)
NOT VALID;

-- ------------------------
-- Geolocation
-- ------------------------
DROP TABLE IF EXISTS public.geolocation_clean CASCADE;

CREATE TABLE public.geolocation_clean (
    geolocation_zip_code_prefix BIGINT NOT NULL,
    geolocation_lat DOUBLE PRECISION NOT NULL,
    geolocation_lng DOUBLE PRECISION NOT NULL,
    geolocation_city TEXT,
    geolocation_state TEXT
);

