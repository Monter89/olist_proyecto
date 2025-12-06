import os
import pandas as pd

BASE_DIR = r"C:\Users\gasto\Documents\BootcampDevlights\olist_proyecto"
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

archivos = os.listdir(RAW_DIR)
print("Archivos encontrados en data/raw:")
for f in archivos:
    print("-", f)

# Ejemplo: leer clientes
clientes_path = os.path.join(RAW_DIR, "olist_customers_dataset.csv")
clientes = pd.read_csv(clientes_path)

print("\nClientes - primeras filas:")
print(clientes.head())

print("\nClientes - info:")
print(clientes.info())

# Ejemplo: leer órdenes
orders_path = os.path.join(RAW_DIR, "olist_orders_dataset.csv")
orders = pd.read_csv(orders_path)

print("\nOrders - primeras filas:")
print(orders.head())

print("\nOrders - info:")
print(orders.info())
