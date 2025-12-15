-- =========================================
-- FINAL ANALYTICS METRICS
-- =========================================

-- -------------------------------------------------
-- 1. Revenue mensual
-- -------------------------------------------------
-- Evolución de ingresos en el tiempo
SELECT
    dt.year_month,
    SUM(f.total_item_value) AS revenue
FROM analytics.fact_order_items f
JOIN analytics.dim_time dt
  ON f.purchase_date = dt.date
GROUP BY dt.year_month
ORDER BY dt.year_month;


-- -------------------------------------------------
-- 2. Cantidad de órdenes por mes
-- -------------------------------------------------
-- Evolución de la demanda
SELECT
    dt.year_month,
    COUNT(DISTINCT f.order_id) AS orders
FROM analytics.fact_order_items f
JOIN analytics.dim_time dt
  ON f.purchase_date = dt.date
GROUP BY dt.year_month
ORDER BY dt.year_month;


-- -------------------------------------------------
-- 3. Revenue por categoría de producto
-- -------------------------------------------------
-- Identifica categorías más rentables
SELECT
    dp.product_category_name_english AS category,
    SUM(f.total_item_value) AS revenue
FROM analytics.fact_order_items f
JOIN analytics.dim_product dp
  ON f.product_id = dp.product_id
GROUP BY dp.product_category_name_english
ORDER BY revenue DESC;


-- -------------------------------------------------
-- 4. Revenue por estado del cliente
-- -------------------------------------------------
-- Distribución geográfica del ingreso
SELECT
    dc.customer_state,
    SUM(f.total_item_value) AS revenue
FROM analytics.fact_order_items f
JOIN analytics.dim_customer dc
  ON f.customer_id = dc.customer_id
GROUP BY dc.customer_state
ORDER BY revenue DESC;


-- -------------------------------------------------
-- 5. Ticket promedio por orden
-- -------------------------------------------------
-- Valor promedio de una orden
SELECT
    AVG(order_total) AS avg_ticket
FROM (
    SELECT
        f.order_id,
        SUM(f.total_item_value) AS order_total
    FROM analytics.fact_order_items f
    GROUP BY f.order_id
) t;


-- -------------------------------------------------
-- 6. Tiempo promedio de entrega (en días)
-- -------------------------------------------------
-- Métrica operativa
SELECT
    AVG(
        o.order_delivered_customer_date
        - o.order_purchase_timestamp
    ) AS avg_delivery_time_days
FROM analytics.dim_order o
WHERE o.order_delivered_customer_date IS NOT NULL;


-- -------------------------------------------------
-- 7. Top 10 productos por revenue
-- -------------------------------------------------
SELECT
    f.product_id,
    SUM(f.total_item_value) AS revenue
FROM analytics.fact_order_items f
GROUP BY f.product_id
ORDER BY revenue DESC
LIMIT 10;


-- -------------------------------------------------
-- 8. Top 10 vendedores por revenue
-- -------------------------------------------------
SELECT
    f.seller_id,
    SUM(f.total_item_value) AS revenue
FROM analytics.fact_order_items f
GROUP BY f.seller_id
ORDER BY revenue DESC
LIMIT 10;
