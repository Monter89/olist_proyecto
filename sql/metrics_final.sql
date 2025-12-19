-- =========================================
-- KPI: Ingresos Totales
-- Objetivo:
-- Calcular el ingreso total generado por la venta de productos.
-- Métrica principal: total_item_value
-- Grano: agregado total
-- Tabla fuente: analytics.fact_order_items
-- Filtro Metabase: fecha_compra
-- =========================================

SELECT
  SUM(total_item_value) AS total_revenue
FROM analytics.fact_order_items
WHERE {{fecha_compra}};

-- =========================================
-- KPI: Total de Órdenes
-- Objetivo:
-- Contar la cantidad de órdenes únicas realizadas.
-- Métrica principal: cantidad de órdenes
-- Grano: agregado total
-- Tabla fuente: analytics.fact_order_items
-- Filtro Metabase: fecha_compra
-- =========================================

SELECT
  COUNT(DISTINCT order_id) AS total_orders
FROM analytics.fact_order_items
WHERE {{fecha_compra}};

-- =========================================
-- KPI: Ticket Promedio
-- Objetivo:
-- Calcular el ingreso promedio por orden.
-- Fórmula: ingresos totales / cantidad de órdenes
-- Grano: agregado total
-- Tabla fuente: analytics.fact_order_items
-- Filtro Metabase: fecha_compra
-- =========================================

SELECT
  SUM(total_item_value)
  / COUNT(DISTINCT order_id) AS avg_ticket
FROM analytics.fact_order_items
WHERE {{fecha_compra}};

-- =========================================
-- Tendencias: Cantidad Total de Ítems Vendidos
-- Objetivo:
-- Contar la cantidad total de ítems vendidos.
-- Métrica: cantidad_items
-- Grano: agregado total
-- Tabla fuente: analytics.fact_order_items
-- Filtro Metabase: fecha
-- =========================================

SELECT
    COUNT(*) AS cantidad_items
FROM analytics.fact_order_items
WHERE 1=1
[[AND {{fecha}}]];


-- =========================================
-- KPI: Costo Promedio de Envío por Orden
-- Objetivo:
-- Calcular el costo promedio de envío considerando el total de freight
-- por orden.
-- Grano: 1 fila por orden (subquery)
-- Tabla fuente: analytics.fact_order_items
-- Filtro Metabase: fecha_compra
-- =========================================


SELECT
  ROUND(
    AVG(t.order_freight),
    2
  ) AS avg_shipping_cost_per_order
FROM (
    SELECT
      order_id,
      SUM(freight_value) AS order_freight
    FROM analytics.fact_order_items
    WHERE {{fecha_compra}}
    GROUP BY order_id
) t;

-- =========================================
-- Tendencia: Ingresos por Categoría
-- Objetivo:
-- Analizar los ingresos generados por cada categoría de producto.
-- Métrica: ingresos totales
-- Dimensión: categoría de producto
-- Permite filtro por categoría específica.
-- =========================================

SELECT
  analytics.dim_product.product_category_name_english AS category,
  SUM(analytics.fact_order_items.total_item_value) AS total_revenue
FROM analytics.fact_order_items
JOIN analytics.dim_product
  ON analytics.fact_order_items.product_id = analytics.dim_product.product_id
WHERE 1=1
[[ AND {{fecha}} ]]
[[ AND analytics.dim_product.product_category_name_english = {{categoria}} ]]
GROUP BY analytics.dim_product.product_category_name_english
ORDER BY total_revenue DESC;


-- =========================================
-- Tendencia: Ingresos en el Tiempo
-- Objetivo:
-- Analizar la evolución mensual de los ingresos.
-- Métrica: total_item_value
-- Dimensión temporal: year_month
-- Tablas: fact_order_items, dim_time
-- =========================================

SELECT
  dt.year_month,
  SUM(analytics.fact_order_items.total_item_value) AS total_revenue
FROM analytics.fact_order_items
JOIN analytics.dim_time dt
  ON analytics.fact_order_items.purchase_date = dt.date
WHERE {{fecha_compra}}
GROUP BY dt.year_month
ORDER BY dt.year_month;


-- =========================================
-- Tendencia: Órdenes en el Tiempo
-- Objetivo:
-- Analizar la evolución mensual de la cantidad de órdenes.
-- Métrica: total de órdenes
-- Dimensión temporal: year_month
-- =========================================

SELECT
  dt.year_month,
  COUNT(DISTINCT order_id) AS total_orders
FROM analytics.fact_order_items 
JOIN analytics.dim_time dt
  ON purchase_date = dt.date
WHERE {{fecha_compra}}
GROUP BY dt.year_month
ORDER BY dt.year_month;

-- =========================================
-- Tendencia: Costo de Envío en el Tiempo
-- Objetivo:
-- Analizar la evolución mensual del costo total de envíos.
-- Métrica: freight_value
-- Dimensión temporal: year_month
-- =========================================

SELECT
  dt.year_month,
  SUM(freight_value) AS total_shipping_cost
FROM analytics.fact_order_items 
JOIN analytics.dim_time dt
  ON purchase_date = dt.date
WHERE {{fecha_compra}}
GROUP BY dt.year_month
ORDER BY dt.year_month;

-- =========================================
-- KPI: Estado de las Órdenes
-- Objetivo:
-- Analizar la distribución de órdenes según su estado.
-- Métrica: cantidad y porcentaje de órdenes
-- =========================================

SELECT
    CASE 
        WHEN order_status IN ('delivered', 'shipped') THEN 'Completadas'
        WHEN order_status IN ('canceled', 'unavailable') THEN 'Canceladas'
        ELSE 'En proceso'
    END AS estado,
    COUNT(DISTINCT order_id) AS cantidad_ordenes,
    ROUND(
        (COUNT(DISTINCT order_id) * 100.0) / SUM(COUNT(DISTINCT order_id)) OVER(),
        2
    ) AS porcentaje
FROM analytics.fact_order_items
WHERE 1=1
    [[AND {{fecha_compra}}]]
GROUP BY 1
ORDER BY cantidad_ordenes DESC;

-- =========================================
-- Rankings: Top 10 Categorías por Ingresos
-- Objetivo:
-- Identificar las categorías de productos con mayor facturación.
-- Métrica: ingresos totales
-- =========================================

SELECT
    product_category_name_english AS categoria,
    SUM(total_item_value) AS ingresos_totales
FROM analytics.fact_order_items
JOIN analytics.dim_product
    ON analytics.fact_order_items.product_id = analytics.dim_product.product_id
WHERE 1=1
  [[AND {{fecha}}]]
GROUP BY product_category_name_english
ORDER BY ingresos_totales DESC
LIMIT 10;

-- =========================================
-- Rankings: Ingresos por Tipo de Pago
-- Objetivo:
-- Analizar cómo se distribuyen los ingresos según el método de pago.
-- Métrica: ingresos totales
-- =========================================

SELECT
    dim_payment.payment_type AS tipo_pago,
    SUM(analytics.fact_order_items.total_item_value) AS ingresos_totales
FROM analytics.fact_order_items
JOIN analytics.dim_payment
    ON analytics.fact_order_items.order_id = dim_payment.order_id
WHERE 1=1
  [[AND {{fecha}}]]
GROUP BY dim_payment.payment_type
ORDER BY ingresos_totales DESC;

-- =========================================
-- Rankings: Costo Total de Envío por Estado
-- Objetivo:
-- Analizar el costo total de envíos por estado.
-- Métrica: freight_value
-- Dimensión geográfica: estado del cliente
-- =========================================

SELECT
    CASE analytics.dim_customer.customer_state
        WHEN 'AC' THEN 'Acre'
        WHEN 'AL' THEN 'Alagoas'
        WHEN 'AP' THEN 'Amapá'
        WHEN 'AM' THEN 'Amazonas'
        WHEN 'BA' THEN 'Bahia'
        WHEN 'CE' THEN 'Ceará'
        WHEN 'DF' THEN 'Distrito Federal'
        WHEN 'ES' THEN 'Espírito Santo'
        WHEN 'GO' THEN 'Goiás'
        WHEN 'MA' THEN 'Maranhão'
        WHEN 'MT' THEN 'Mato Grosso'
        WHEN 'MS' THEN 'Mato Grosso do Sul'
        WHEN 'MG' THEN 'Minas Gerais'
        WHEN 'PA' THEN 'Pará'
        WHEN 'PB' THEN 'Paraíba'
        WHEN 'PR' THEN 'Paraná'
        WHEN 'PE' THEN 'Pernambuco'
        WHEN 'PI' THEN 'Piauí'
        WHEN 'RJ' THEN 'Rio de Janeiro'
        WHEN 'RN' THEN 'Rio Grande do Norte'
        WHEN 'RS' THEN 'Rio Grande do Sul'
        WHEN 'RO' THEN 'Rondônia'
        WHEN 'RR' THEN 'Roraima'
        WHEN 'SC' THEN 'Santa Catarina'
        WHEN 'SE' THEN 'Sergipe'
        WHEN 'SP' THEN 'São Paulo'
        WHEN 'TO' THEN 'Tocantins'
        ELSE 'No informado'
    END AS estado,
    SUM(analytics.fact_order_items.freight_value) AS costo_envio_total
FROM analytics.fact_order_items
JOIN analytics.dim_customer
    ON analytics.fact_order_items.customer_id = analytics.dim_customer.customer_id
WHERE 1=1
  [[AND {{fecha}}]]
GROUP BY analytics.dim_customer.customer_state
ORDER BY costo_envio_total DESC
LIMIT 15;

-- =========================================
-- Segmentacion: Ingresos por Estado (Mapa)
-- Objetivo:
-- Analizar ingresos, órdenes y clientes por estado.
-- Incluye latitud y longitud para visualización en mapas.
-- =========================================

SELECT 
    analytics.dim_customer.customer_state AS estado,
    COUNT(DISTINCT analytics.fact_order_items.customer_id) AS cantidad_clientes,
    COUNT(DISTINCT analytics.fact_order_items.order_id) AS ordenes,
    SUM(analytics.fact_order_items.total_item_value) AS ingresos_totales,
    ROUND(AVG(analytics.fact_order_items.total_item_value), 2) AS ticket_promedio,
    CASE analytics.dim_customer.customer_state
        WHEN 'AC' THEN -9.97499
        WHEN 'AL' THEN -9.66599
        WHEN 'AP' THEN 0.03493
        WHEN 'AM' THEN -3.11903
        WHEN 'BA' THEN -12.9714
        WHEN 'CE' THEN -3.71722
        WHEN 'DF' THEN -15.79389
        WHEN 'ES' THEN -20.3155
        WHEN 'GO' THEN -16.6864
        WHEN 'MA' THEN -2.52972
        WHEN 'MT' THEN -15.6010
        WHEN 'MS' THEN -20.4697
        WHEN 'MG' THEN -19.9167
        WHEN 'PA' THEN -1.45583
        WHEN 'PB' THEN -7.1195
        WHEN 'PR' THEN -25.4284
        WHEN 'PE' THEN -8.04756
        WHEN 'PI' THEN -5.08921
        WHEN 'RJ' THEN -22.9068
        WHEN 'RN' THEN -5.79448
        WHEN 'RS' THEN -30.0346
        WHEN 'RO' THEN -8.76077
        WHEN 'RR' THEN 2.82384
        WHEN 'SC' THEN -27.5954
        WHEN 'SE' THEN -10.9472
        WHEN 'SP' THEN -23.5505
        WHEN 'TO' THEN -10.2491
    END AS latitud,
    CASE analytics.dim_customer.customer_state
        WHEN 'AC' THEN -67.8243
        WHEN 'AL' THEN -35.7350
        WHEN 'AP' THEN -51.0694
        WHEN 'AM' THEN -60.0217
        WHEN 'BA' THEN -38.5014
        WHEN 'CE' THEN -38.5434
        WHEN 'DF' THEN -47.88278
        WHEN 'ES' THEN -40.3128
        WHEN 'GO' THEN -49.2643
        WHEN 'MA' THEN -44.3028
        WHEN 'MT' THEN -56.0974
        WHEN 'MS' THEN -54.6201
        WHEN 'MG' THEN -43.9345
        WHEN 'PA' THEN -48.4898
        WHEN 'PB' THEN -34.8641
        WHEN 'PR' THEN -49.2733
        WHEN 'PE' THEN -34.8770
        WHEN 'PI' THEN -42.8016
        WHEN 'RJ' THEN -43.1729
        WHEN 'RN' THEN -35.2110
        WHEN 'RS' THEN -51.2177
        WHEN 'RO' THEN -63.8999
        WHEN 'RR' THEN -60.6753
        WHEN 'SC' THEN -48.5480
        WHEN 'SE' THEN -37.0731
        WHEN 'SP' THEN -46.6333
        WHEN 'TO' THEN -48.3243
    END AS longitud
FROM analytics.fact_order_items
JOIN analytics.dim_customer
    ON analytics.fact_order_items.customer_id = analytics.dim_customer.customer_id
WHERE 1=1 [[AND {{fecha}}]]
GROUP BY analytics.dim_customer.customer_state
ORDER BY ingresos_totales DESC;

