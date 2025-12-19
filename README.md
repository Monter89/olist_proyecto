# 📊 Proyecto Olist – Data Analytics

## 📌 Descripción general

Este proyecto consiste en el desarrollo de una **solución de análisis de datos end-to-end** a partir de un dataset real de e‑commerce (Olist – Brasil). El objetivo principal es transformar datos transaccionales en información analítica útil para la **toma de decisiones de negocio**, aplicando procesos de ETL, modelado dimensional y visualización mediante dashboards.

El proyecto fue realizado en el marco del **Bootcamp de Data Analytics 2025**.

---

## 🎯 Objetivos del proyecto

* Realizar la **ingesta, limpieza y transformación** de datos reales de e‑commerce.
* Persistir los datos en una **base de datos relacional (PostgreSQL)**.
* Diseñar un **Data Warehouse** con modelo dimensional (esquema estrella).
* Construir métricas e indicadores clave de negocio.
* Visualizar los resultados mediante **dashboards interactivos en Metabase**.

---

## 🗂️ Dataset utilizado

* **Fuente:** Olist (dataset público de e‑commerce brasileño)
* **Período:** 2016 – 2018
* **Contenido:**

  * Órdenes de venta
  * Clientes y vendedores
  * Productos y categorías
  * Pagos
  * Envíos y tiempos de entrega
  * Opiniones de clientes
* **Volumen:** Más de 100.000 pedidos históricos

---

## 🧱 Arquitectura del proyecto

## 🧱 Arquitectura del proyecto

<p align="center">
  <img src="assets/arquitectura_olist.png" alt="Arquitectura del proyecto Olist" width="900">
</p>

<p align="center">
  <em>Arquitectura end-to-end del proyecto: ingesta, transformación, almacenamiento y visualización.</em>
</p>


---

## 🧹 Procesos de limpieza y transformación (ETL)

Durante el proceso de ETL se aplicaron las siguientes transformaciones:

* 🗑 Deduplicación de registros
* 📅 Normalización y validación de fechas
* 🧹 Tratamiento de valores nulos
* 📐 Normalización de strings
* ✅ Imputación de valores faltantes (moda)
* 📊 Detección y control de valores atípicos
* 🔗 Validación de integridad entre tablas

Estas transformaciones permitieron mejorar la calidad de los datos y garantizar métricas consistentes para el análisis.

---

## 🧠 Modelo analítico

El Data Warehouse fue diseñado utilizando un **esquema estrella**, compuesto por:

### 🔹 Tabla de hechos

* **fact_order_items**

  * Grain: 1 fila = 1 ítem vendido
  * Métricas: precio, costo de envío, valor total por ítem

### 🔹 Dimensiones

* **dim_time** – análisis temporal
* **dim_product** – productos y categorías
* **dim_customer** – clientes
* **dim_seller** – vendedores
* **dim_order** – estado y fechas de órdenes
* **dim_payment** – medio de pago
* **dim_zip_codes** – información geográfica

Este modelo permite analizar el negocio desde múltiples perspectivas de forma eficiente.

---

## 📊 Dashboards y métricas

Los dashboards desarrollados en Metabase permiten responder preguntas clave como:

* ¿Cuál es el ingreso total generado?
* ¿Cuántas órdenes se realizaron?
* ¿Cuál es el ticket promedio por orden?
* ¿Cuál es el costo promedio de envío?
* ¿Qué porcentaje de órdenes se completan exitosamente?
* ¿Cómo evolucionan los ingresos y las órdenes en el tiempo?
* ¿Qué categorías generan mayor revenue?
* ¿En qué regiones se concentra la actividad comercial?

Los dashboards están organizados en:

* KPIs generales
* Tendencias temporales
* Segmentación
* Rankings

---

## 🛠️ Tecnologías utilizadas

* **Python** (ETL y limpieza de datos)
* **Pandas / NumPy**
* **PostgreSQL**
* **Docker & Docker Compose**
* **Metabase**
* **SQL**

---

## 🚀 Oportunidades de mejora

* Escalabilidad del procesamiento con **Apache Spark**
* Migración del Data Warehouse a la **nube** (BigQuery, Redshift, Synapse)
* Automatización de pipelines con **Apache Airflow**
* Integración de nuevas fuentes de datos

---

## 🧾 Autor

**Gaston Montero**
**Rodrigo Buccicardi**
Bootcamp de Data Analytics – 2025

---

⭐ *Este proyecto demuestra cómo un enfoque analítico bien diseñado puede transformar datos en valor para el negocio.*

