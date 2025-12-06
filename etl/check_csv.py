import pandas as pd
import os

BASE_DIR = r"C:\Users\gasto\Documents\BootcampDevlights\olist_proyecto"
data_dir = os.path.join(BASE_DIR, "data", "raw")

df = pd.read_csv(os.path.join(data_dir, "product_category_name_translation.csv"), encoding="latin1")

print(df.columns)
