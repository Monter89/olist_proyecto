# 📊 Proyecto Olist – Data Analytics 

## 🧠 Descripción general
Este proyecto trabaja sobre el **dataset real de e-commerce brasileño Olist**, con un enfoque práctico de **Data Engineering + Analytics**.

El objetivo es:
- limpiar y preparar datos reales (con errores e inconsistencias),
- cargarlos en PostgreSQL,
- construir un **modelo analítico tipo estrella**,
- y dejar métricas listas para visualización en BI (Metabase).

El proyecto está pensado como un **trabajo colaborativo**, donde la capa de datos y la capa de BI están bien separadas.

---

## 🧱 Arquitectura del proyecto

CSV (raw)
↓
ETL en Python (Pandas)
↓
PostgreSQL (tablas *_clean)
↓
Schema analytics (views: dims + fact)
↓
Métricas SQL
↓
Metabase / BI


---

## 🔄 ETL – Limpieza de datos

El pipeline ETL está implementado en **Python + Pandas** (`etl/clean_pipeline.py`).

### Principales decisiones de limpieza:
- Eliminación de duplicados por clave lógica.
- Conversión explícita de tipos.
- Normalización de textos (encoding, mayúsculas/minúsculas).
- Validación de valores numéricos (no negativos).
- **Corrección de fechas inválidas** (ej: `32/13/2020`) en lugar de descartar filas.
- Separación clara entre datos **raw** y **clean**.

👉 El objetivo no es “embellecer” datos, sino **hacerlos utilizables y defendibles**.

---

## 🗄️ Base de datos – PostgreSQL

Los datos limpios se cargan en PostgreSQL como tablas `*_clean`.

Ejemplos:
- `orders_clean`
- `order_items_clean`
- `customers_clean`
- `products_clean`
- `sellers_clean`

No se forzaron **FKs ni índices** por decisión de diseño (dataset moderado y foco en modelado).

---

## ⭐ Modelo analítico (Schema `analytics`)

Se construyó un **modelo estrella** usando **VIEWS** (no tablas físicas).

### 📌 Dimensiones
- `analytics.dim_time`
- `analytics.dim_customer`
- `analytics.dim_product`
- `analytics.dim_seller`
- `analytics.dim_order`

### 📌 Tabla de hechos
- `analytics.fact_order_items`

**Grano de la fact**  
> 1 fila = 1 ítem vendido dentro de una orden

Las vistas están definidas en:

sql/analytics_model.sql

Esto permite:
- reproducibilidad,
- flexibilidad,
- y no modificar datos base.

---

## ⚠️ Nota importante sobre el dataset
El dataset Olist contiene **inconsistencias reales**:
- existen `order_items` sin `order` asociada.

Decisión tomada:
- la **fact view usa INNER JOIN**, excluyendo registros huérfanos,
- no se borran datos base,
- la decisión queda documentada y es reversible.

---

## 📊 Métricas finales

Las métricas están definidas en:


sql/metrics_final.sql


Incluyen:
1. Revenue mensual
2. Cantidad de órdenes por mes
3. Revenue por categoría
4. Revenue por estado del cliente
5. Ticket promedio
6. Tiempo promedio de entrega
7. Top productos por revenue
8. Top vendedores por revenue

Todas se basan en:


analytics.fact_order_items + dimensiones


---

## 📈 Metabase / BI

La visualización se realiza en **Metabase**.

📌 Recomendaciones:
- Usar `analytics.fact_order_items` como tabla base.
- Cruces mediante dimensiones.
- No usar tablas `*_clean` directamente para dashboards.

Más detalles en `METABASE.md`.

---

## 🧠 Objetivo del proyecto
Este proyecto busca demostrar:
- criterio técnico,
- separación de responsabilidades,
- modelado analítico correcto,
- y trabajo colaborativo real.

No está orientado solo a visualizaciones, sino a **calidad de datos y diseño**.

---

## 👥 Trabajo en equipo
- **ETL + modelo analítico:** este repositorio
- **BI / dashboards:** Metabase

El proyecto queda abierto a revisión y mejoras.