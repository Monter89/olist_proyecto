-- ============================
-- LOAD CLEAN DATA (COPY)
-- ============================

TRUNCATE TABLE public.customers_clean;
COPY public.customers_clean
FROM '/clean/customers_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.orders_clean;
COPY public.orders_clean
FROM '/clean/orders_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.products_clean;
COPY public.products_clean
FROM '/clean/products_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.categories_clean;
COPY public.categories_clean
FROM '/clean/categories_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.sellers_clean;
COPY public.sellers_clean
FROM '/clean/sellers_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.order_items_clean;
COPY public.order_items_clean
FROM '/clean/order_items_clean.csv'
DELIMITER ','
CSV HEADER;


TRUNCATE TABLE public.payments_clean;
COPY public.payments_clean
FROM '/clean/payments_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.reviews_clean;
COPY public.reviews_clean
FROM '/clean/reviews_clean.csv'
DELIMITER ','
CSV HEADER;

TRUNCATE TABLE public.geolocation_clean;
COPY public.geolocation_clean
FROM '/clean/geolocation_clean.csv'
DELIMITER ','
CSV HEADER;
