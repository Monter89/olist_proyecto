# Metabase – Olist Analytics

## Base de datos
- Motor: PostgreSQL
- Esquema analítico: `analytics`
- Tablas/Vistas principales:
  - fact_order_items
  - dim_time
  - dim_customer
  - dim_product
  - dim_seller
  - dim_order

## Modelo
- Modelo estrella
- Grano de la fact: 1 fila = 1 ítem vendido
- Las métricas deben basarse en `analytics.fact_order_items`
- Usar INNER JOIN con dimensiones

## Métricas sugeridas
1. Revenue mensual  
2. Órdenes por mes  
3. Revenue por categoría  
4. Revenue por estado del cliente  
5. Ticket promedio  
6. Tiempo promedio de entrega

## Notas importantes
- Existen order_items sin order asociada en el dataset original.
- La fact view ya excluye esos registros.
- No se forzaron índices ni FKs por decisión de diseño.
