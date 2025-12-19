-- ============================
-- LOAD CLEAN DATA (COPY)
-- ============================

-- Truncar todas las tablas de una vez con CASCADE
TRUNCATE TABLE 
    public.categories_clean,
    public.customers_clean,
    public.sellers_clean,
    public.products_clean,
    public.orders_clean,
    public.order_items_clean,
    public.payments_clean,
    public.reviews_clean,
    public.geolocation_clean
CASCADE;

-- Cargar en orden: primero las que no tienen dependencias, luego las dependientes
COPY public.categories_clean
FROM '/clean/categories_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.customers_clean
FROM '/clean/customers_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.sellers_clean
FROM '/clean/sellers_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.products_clean
FROM '/clean/products_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.orders_clean
FROM '/clean/orders_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.order_items_clean
FROM '/clean/order_items_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.payments_clean
FROM '/clean/payments_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.reviews_clean
FROM '/clean/reviews_clean.csv'
DELIMITER ','
CSV HEADER;

COPY public.geolocation_clean
FROM '/clean/geolocation_clean.csv'
DELIMITER ','
CSV HEADER;