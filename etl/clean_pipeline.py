import pandas as pd
import numpy as np
import unicodedata
from pathlib import Path
from calendar import monthrange

# -----------------------
# Paths
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"


# -----------------------
# Load function
# -----------------------
def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    return pd.read_csv(path)


# -----------------------
# Helpers
# -----------------------
ESTADOS_BRASIL = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

def normalizar_string(valor):
    """Normaliza strings limpiando encoding, espacios y caracteres especiales."""
    if pd.isna(valor):
        return np.nan
    
    valor = str(valor).strip()
    
    # Detectar valores nulos
    valores_nulos = ['NONE', 'NÃNE', 'NÃ³NE', 'NAN', 'NULL', 'N/A', 'NA', '']
    if valor.upper() in valores_nulos:
        return np.nan
    
    # Corregir encoding
    try:
        valor = valor.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')
    except:
        pass
    
    # Normalizar Unicode y eliminar acentos
    valor = unicodedata.normalize('NFKD', valor)
    valor = valor.encode('ASCII', 'ignore').decode('ASCII')
    valor = ' '.join(valor.split())
    
    return np.nan if valor == '' else valor


def corregir_fecha_invalida(serie):
    """
    Parsea fechas en múltiples formatos.
    Si la fecha es inválida (mes > 12 o componentes fuera de rango), devuelve NaT.
    """
    # 0. Limpiar la serie antes de parsear
    serie_limpia = serie.astype(str).str.strip()
    
    # 1. Primer intento: conversión estándar (captura ISO y formatos estándar)
    resultado = pd.to_datetime(serie_limpia, errors='coerce')
    
    # 2. Segundo intento: para los que fallaron, intentar con dayfirst=True (formato brasileño DD/MM/YYYY)
    mask_fallidos = resultado.isna() & serie.notna()
    if mask_fallidos.sum() > 0:
        resultado[mask_fallidos] = pd.to_datetime(serie_limpia[mask_fallidos], errors='coerce', dayfirst=True)

    # 3. Identificar los que TODAVÍA fallan y tienen '/' (posible formato DD/MM/YYYY problemático)
    mask_fallidos = resultado.isna() & serie.notna()
    mask_con_barra = serie_limpia.str.contains('/', na=False)
    mask_procesar = mask_fallidos & mask_con_barra

    if mask_procesar.sum() == 0:
        return resultado

    # 4. Procesar cadenas con '/' de forma estricta
    def procesar_dd_mm_yyyy(fecha_str):
        try:
            # Limpiar espacios en blanco
            fecha_str = str(fecha_str).strip()
            
            # Separar fecha y hora (si existe)
            partes = fecha_str.split()
            fecha_parte = partes[0]
            hora_parte = partes[1] if len(partes) > 1 and partes[1] else '00:00:00'

            componentes = fecha_parte.split('/')
            if len(componentes) != 3:
                return pd.NaT

            day, month, year = map(int, componentes)

            # Si el mes es inválido, devolvemos NaT
            if month < 1 or month > 12:
                return pd.NaT

            # Validar rango de años (2016-2018)
            if year < 2016 or year > 2018:
                return pd.NaT

            # Validar el día según el mes y año
            max_day = monthrange(year, month)[1]
            if day < 1 or day > max_day:
                return pd.NaT

            # Reconstruir en formato estándar
            fecha_corregida = f"{year}-{month:02d}-{day:02d} {hora_parte}"
            return pd.to_datetime(fecha_corregida)

        except:
            return pd.NaT

    # Aplicar solo a los registros problemáticos
    resultado[mask_procesar] = serie_limpia[mask_procesar].apply(procesar_dd_mm_yyyy)

    return resultado


def imputar_zip_code(df, zip_col, city_col, state_col):
    """Imputa zip codes inválidos (NaN o <= 0) usando moda por ciudad/estado."""
    df = df.copy()
    
    # Crear lookups con valores válidos
    zip_por_ciudad_estado = (
        df[df[zip_col] > 0]
        .groupby([city_col, state_col])[zip_col]
        .agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else np.nan)
        .to_dict()
    )
    
    zip_por_estado = (
        df[df[zip_col] > 0]
        .groupby(state_col)[zip_col]
        .agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else np.nan)
        .to_dict()
    )
    
    # Imputar
    mask_imputar = df[zip_col].isna() | (df[zip_col] <= 0)
    
    for idx in df[mask_imputar].index:
        city = df.loc[idx, city_col]
        state = df.loc[idx, state_col]
        
        # Intentar por ciudad+estado
        if pd.notna(city) and pd.notna(state):
            zip_imputado = zip_por_ciudad_estado.get((city, state))
            if pd.notna(zip_imputado):
                df.loc[idx, zip_col] = zip_imputado
                continue
        
        # Fallback por estado
        if pd.notna(state):
            zip_imputado = zip_por_estado.get(state)
            if pd.notna(zip_imputado):
                df.loc[idx, zip_col] = zip_imputado
    
    return df


# -----------------------
# Customers
# -----------------------
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza datos de customers."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all')
    df = df.drop_duplicates()

    # Normalizar customer_id
    df['customer_id'] = df['customer_id'].apply(normalizar_string)
    df = df[df['customer_id'].notna()]
    df = df.drop_duplicates(subset='customer_id', keep = "first")

    # Normalizar customer_city
    df['customer_city'] = (
        df['customer_city']
        .apply(normalizar_string)
        .str.lower()
        .str.title()
    )

    # Normalizar y validar customer_state
    df['customer_state'] = df['customer_state'].apply(normalizar_string).str.upper()
    df.loc[~df['customer_state'].isin(ESTADOS_BRASIL), 'customer_state'] = np.nan

    # Eliminar FAKE_KEY sin datos geográficos
    df = df[
        ~(
            df['customer_id'].str.contains('FAKE_KEY', na=False) &
            df['customer_city'].isna() &
            df['customer_state'].isna()
        )
    ]

    df.loc[
        (df['customer_zip_code_prefix'] <= 0) |
        (df['customer_zip_code_prefix'] > 99999),
        'customer_zip_code_prefix'
    ] = np.nan

    # Imputar zip codes inválidos
    df = imputar_zip_code(df, 'customer_zip_code_prefix', 'customer_city', 'customer_state')

    # Limpiar columnas innecesarias y formatear
    df = df.drop('noise_flag', axis=1, errors='ignore')

    # Capitalizar ciudad
    df['customer_city'] = df['customer_city'].str.title()

    df['customer_zip_code_prefix'] = df['customer_zip_code_prefix'].astype('Int64')

    return df


# -----------------------
# Orders
# -----------------------
def clean_orders(df: pd.DataFrame, valid_customer_ids: set = None) -> pd.DataFrame:
    """Limpia y normaliza datos de órdenes."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar IDs y status
    df['order_id'] = df['order_id'].apply(normalizar_string)
    df['customer_id'] = df['customer_id'].apply(normalizar_string)
    df['order_status'] = df['order_status'].apply(normalizar_string).str.lower()

    # Eliminar registros sin order_id y duplicados
    df = df[df['order_id'].notna()]

    # Filtrar por customer_ids válidos (integridad referencial)
    if valid_customer_ids is not None:
        before = len(df)
        df = df[df['customer_id'].isin(valid_customer_ids)]
        print(f"  Removed {before - len(df)} orders with invalid customer_id")

    df = df.drop_duplicates(subset='order_id')

    # Convertir columnas de fechas
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for col in date_columns:
        df[col] = corregir_fecha_invalida(df[col])
    
    # Validación de rango de fechas (red de seguridad)
    fecha_min = pd.Timestamp('2016-01-01')
    fecha_max = pd.Timestamp('2018-12-31')
    
    for col in date_columns:
        mask_fuera_rango = (
            df[col].notna() & 
            ((df[col] < fecha_min) | (df[col] > fecha_max))
        )
        if mask_fuera_rango.sum() > 0:
            df.loc[mask_fuera_rango, col] = pd.NaT

    # approved >= purchase (corregir si approved < purchase)
    mask = (
        df['order_approved_at'].notna() &
        df['order_purchase_timestamp'].notna() &
        (df['order_approved_at'] < df['order_purchase_timestamp'])
    )
    if mask.sum() > 0:
        df.loc[mask, 'order_approved_at'] = df.loc[mask, 'order_purchase_timestamp']

    # carrier >= approved
    mask = (
        df['order_delivered_carrier_date'].notna() &
        df['order_approved_at'].notna() &
        (df['order_delivered_carrier_date'] < df['order_approved_at'])
    )
    if mask.sum() > 0:
        df.loc[mask, 'order_delivered_carrier_date'] = pd.NaT

    # customer >= carrier
    mask = (
        df['order_delivered_customer_date'].notna() &
        df['order_delivered_carrier_date'].notna() &
        (df['order_delivered_customer_date'] < df['order_delivered_carrier_date'])
    )
    if mask.sum() > 0:
        df.loc[mask, 'order_delivered_customer_date'] = pd.NaT

    # Limpiar columnas innecesarias
    df = df.drop('noise_flag', axis=1, errors='ignore')

    return df


# -----------------------
# Order Items
# -----------------------
def clean_order_items(df: pd.DataFrame, valid_order_ids: set = None, valid_product_ids: set = None, valid_seller_ids: set = None) -> pd.DataFrame:
    """Limpia y normaliza datos de ítems de órdenes."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar IDs
    df['order_id'] = df['order_id'].apply(normalizar_string)
    df['product_id'] = df['product_id'].apply(normalizar_string)
    df['seller_id'] = df['seller_id'].apply(normalizar_string)

    # Eliminar registros sin IDs críticos
    df = df[df['order_id'].notna() & df['product_id'].notna()]

    # Filtrar por IDs válidos (integridad referencial)
    if valid_order_ids is not None:
        before = len(df)
        df = df[df['order_id'].isin(valid_order_ids)]
        print(f"  Removed {before - len(df)} order_items with invalid order_id")
    
    if valid_product_ids is not None:
        before = len(df)
        df = df[df['product_id'].isin(valid_product_ids)]
        print(f"  Removed {before - len(df)} order_items with invalid product_id")
    
    if valid_seller_ids is not None:
        before = len(df)
        df = df[df['seller_id'].isin(valid_seller_ids)]
        print(f"  Removed {before - len(df)} order_items with invalid seller_id")

    # Eliminar duplicados por order_id + order_item_id
    df = df.drop_duplicates(subset=['order_id', 'order_item_id'])

    # Convertir fecha
    df['shipping_limit_date'] = corregir_fecha_invalida(df['shipping_limit_date'])

    # Limpiar valores numéricos inválidos
    df.loc[df['price'] < 0, 'price'] = np.nan
    df.loc[df['price'] > 50000, 'price'] = np.nan
    df.loc[df['freight_value'] < 0, 'freight_value'] = np.nan
    df.loc[df['freight_value'] > 10000, 'freight_value'] = np.nan

    # Eliminar registros sin price (crítico)
    df = df[df['price'].notna()]

    # Limpiar columnas innecesarias
    df = df.drop('noise_flag', axis=1, errors='ignore')

    return df


# -----------------------
# Payments
# -----------------------
def clean_payments(df: pd.DataFrame, valid_order_ids: set = None) -> pd.DataFrame:
    """Limpia y normaliza datos de pagos."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar IDs y payment_type
    df['order_id'] = df['order_id'].apply(normalizar_string)
    df['payment_type'] = df['payment_type'].apply(normalizar_string).str.lower()

    # Eliminar registros sin order_id
    df = df[df['order_id'].notna()]

    # Filtrar por order_ids válidos
    if valid_order_ids is not None:
        before = len(df)
        df = df[df['order_id'].isin(valid_order_ids)]
        print(f"  Removed {before - len(df)} payments with invalid order_id")

    # Eliminar duplicados por order_id + payment_sequential
    df = df.drop_duplicates(subset=['order_id', 'payment_sequential'])

    # Limpiar valores numéricos inválidos
    df.loc[(df['payment_sequential'] < 1) | (df['payment_sequential'] > 100), 'payment_sequential'] = np.nan
    df.loc[(df['payment_installments'] < 1) | (df['payment_installments'] > 24), 'payment_installments'] = np.nan
    df.loc[(df['payment_value'] <= 0) | (df['payment_value'] > 50000), 'payment_value'] = np.nan

    # Eliminar registros sin payment_value
    df = df[df['payment_value'].notna()]

    # Limpiar columnas innecesarias
    df = df.drop('noise_flag', axis=1, errors='ignore')

    return df


# -----------------------
# Products
# -----------------------
def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza datos de productos."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar IDs y categorías
    df['product_id'] = df['product_id'].apply(normalizar_string)
    df['product_category_name'] = df['product_category_name'].apply(normalizar_string)

    # Corregir typos y duplicados en categorías
    correcciones_categorias = {
        'electrncos': 'eletronicos',
        'ELETRONICOOS': 'eletronicos',
        'Electronics': 'eletronicos',
        'categria': 'eletronicos',
        'casa_conforto_2': 'casa_conforto',
        'eletrodomesticos_2': 'eletrodomesticos',
        'nan': None
    }

    df['product_category_name'] = df['product_category_name'].replace(correcciones_categorias)

    # Eliminar registros sin product_id
    df = df[df['product_id'].notna()]

    # Eliminar duplicados por product_id
    df = df.drop_duplicates(subset='product_id')

    numeric_cols = [
        'product_name_lenght', 
        'product_description_lenght', 
        'product_photos_qty',
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[(df[col] < 0) | (df[col] > 50000), col] = np.nan

    # Limpiar columnas innecesarias
    df = df.drop('noise_flag', axis=1, errors='ignore')

    return df


# -----------------------
# Reviews
# -----------------------
def clean_reviews(df: pd.DataFrame, valid_order_ids: set = None) -> pd.DataFrame:
    """Limpia y normaliza datos de reviews."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar IDs y comentarios
    df['review_id'] = df['review_id'].apply(normalizar_string)
    df['order_id'] = df['order_id'].apply(normalizar_string)
    df['review_comment_title'] = df['review_comment_title'].apply(normalizar_string)
    df['review_comment_message'] = df['review_comment_message'].apply(normalizar_string)

    # Eliminar registros sin IDs críticos
    df = df[df['review_id'].notna() & df['order_id'].notna()]

    # Filtrar por order_ids válidos
    if valid_order_ids is not None:
        before = len(df)
        df = df[df['order_id'].isin(valid_order_ids)]
        print(f"  Removed {before - len(df)} reviews with invalid order_id")

    # Eliminar duplicados por review_id
    df = df.drop_duplicates(subset='review_id')

    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")
    df = df[df["review_score"].between(1, 5)]

    # Convertir fechas
    df['review_creation_date'] = corregir_fecha_invalida(df['review_creation_date'])
    df['review_answer_timestamp'] = corregir_fecha_invalida(df['review_answer_timestamp'])

    # Validar lógica temporal: answer >= creation
    mask = (
        df['review_answer_timestamp'].notna() &
        df['review_creation_date'].notna() &
        (df['review_answer_timestamp'] < df['review_creation_date'])
    )
    if mask.sum() > 0:
        df.loc[mask, 'review_answer_timestamp'] = pd.NaT

    # Limpiar columnas innecesarias
    df = df.drop('noise_flag', axis=1, errors='ignore')

    return df


# -----------------------
# Sellers
# -----------------------
def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza datos de vendedores."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar seller_id y ubicación
    df['seller_id'] = df['seller_id'].apply(normalizar_string)
    df['seller_city'] = df['seller_city'].apply(normalizar_string).str.lower()
    df['seller_state'] = df['seller_state'].apply(normalizar_string).str.upper()

    # Validar seller_state contra estados brasileños
    df.loc[~df['seller_state'].isin(ESTADOS_BRASIL), 'seller_state'] = np.nan

    # Eliminar registros sin seller_id
    df = df[df['seller_id'].notna()]

    # Eliminar duplicados por seller_id
    df = df.drop_duplicates(subset='seller_id')

    # Limpiar seller_zip_code_prefix inválidos ANTES de imputar
    df.loc[
        (df['seller_zip_code_prefix'] <= 0) | 
        (df['seller_zip_code_prefix'] > 99999), 
        'seller_zip_code_prefix'
    ] = np.nan
    
    # Imputar seller_zip_code_prefix
    df = imputar_zip_code(df, 'seller_zip_code_prefix', 'seller_city', 'seller_state')
    
    # Limpiar y formatear columnas finales
    df = df.drop('noise_flag', axis=1, errors='ignore')

    df['seller_city'] = df['seller_city'].str.title()

    df['seller_zip_code_prefix'] = df['seller_zip_code_prefix'].astype('Int64')

    return df


# -----------------------
# Geolocation
# -----------------------
def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza datos de geolocalización."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar city y state
    df['geolocation_city'] = df['geolocation_city'].apply(normalizar_string).str.title()
    df['geolocation_state'] = df['geolocation_state'].apply(normalizar_string).str.upper()

    # Validar geolocation_state contra estados brasileños
    df.loc[~df['geolocation_state'].isin(ESTADOS_BRASIL), 'geolocation_state'] = np.nan

    # Convertir coordenadas a float
    df['geolocation_lat'] = pd.to_numeric(df['geolocation_lat'], errors='coerce')
    df['geolocation_lng'] = pd.to_numeric(df['geolocation_lng'], errors='coerce')

    # Limpiar geolocation_zip_code_prefix inválidos
    df.loc[
        (df['geolocation_zip_code_prefix'] <= 0) | 
        (df['geolocation_zip_code_prefix'] > 99999), 
        'geolocation_zip_code_prefix'
    ] = np.nan

    # Limpiar coordenadas inválidas (Brasil: lat -34 a 6, lng -75 a -33)
    df.loc[
        (df['geolocation_lat'] < -34) | 
        (df['geolocation_lat'] > 6), 
        'geolocation_lat'
    ] = np.nan

    df.loc[
        (df['geolocation_lng'] < -75) | 
        (df['geolocation_lng'] > -33), 
        'geolocation_lng'
    ] = np.nan

    # Eliminar registros sin datos críticos
    df = df[
        df['geolocation_zip_code_prefix'].notna() &
        df['geolocation_lat'].notna() &
        df['geolocation_lng'].notna()
    ]

    # Formatear columnas finales
    df = df.drop('noise_flag', axis=1, errors='ignore')

    df['geolocation_zip_code_prefix'] = df['geolocation_zip_code_prefix'].astype('Int64')

    return df


# -----------------------
# Category Translation
# -----------------------
def clean_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza datos de traducción de categorías."""
    df = df.copy()

    # Eliminar filas vacías y duplicados
    df = df.dropna(how='all').drop_duplicates()

    # Normalizar ambas columnas
    df['product_category_name'] = df['product_category_name'].apply(normalizar_string).str.lower()
    df['product_category_name_english'] = df['product_category_name_english'].apply(normalizar_string).str.lower()

    # Corregir typos y duplicados semánticos
    correcciones_pt = {
        'electrncos': 'eletronicos',
        'eletronicoos': 'eletronicos',
        'categria': 'eletronicos',
        'casa_conforto_2': 'casa_conforto'
    }
    
    correcciones_en = {
        'eletronicos': 'electronics',
        'eletronicoos': 'electronics',
        'costruction_tools_tools': 'construction_tools_tools',
        'costruction_tools_garden': 'construction_tools_garden',
        'home_comfort_2': 'home_comfort',
        'home_confort': 'home_comfort',
        'construction_tools_tools': 'construction_tools',
        'la_cuisine': 'kitchen',
        'market_place': 'marketplace'
    }
    
    df['product_category_name'] = df['product_category_name'].replace(correcciones_pt)
    df['product_category_name_english'] = df['product_category_name_english'].replace(correcciones_en)

    # Eliminar registros sin product_category_name
    df = df[df['product_category_name'].notna()]
    
    # Eliminar duplicados por product_category_name
    df = df.drop_duplicates(subset='product_category_name')
    
    # Agregar nuevas traducciones faltantes
    nuevas_traducciones = pd.DataFrame([
        {'product_category_name': 'automotivo', 'product_category_name_english': 'automotive'},
        {'product_category_name': 'beleza_saude', 'product_category_name_english': 'health_beauty'},
        {'product_category_name': 'cool_stuff', 'product_category_name_english': 'cool_stuff'},
        {'product_category_name': 'eletroportateis', 'product_category_name_english': 'small_appliances'},
        {'product_category_name': 'papelaria', 'product_category_name_english': 'stationery'},
        {'product_category_name': 'moveis_decoracao', 'product_category_name_english': 'furniture_decor'},
        {'product_category_name': 'alimentos_bebidas', 'product_category_name_english': 'food_drinks'},
        {'product_category_name': 'construcao_ferramentas_seguranca', 'product_category_name_english': 'construction_tools_safety'},
        {'product_category_name': 'fashion_esporte', 'product_category_name_english': 'fashion_sport'},
        {'product_category_name': 'fashion_roupa_feminina', 'product_category_name_english': 'fashion_female_clothing'},
        {'product_category_name': 'fashion_underwear_e_moda_praia', 'product_category_name_english': 'fashion_underwear_beach'},
        {'product_category_name': 'pc_gamer', 'product_category_name_english': 'gaming_pc'},
        {'product_category_name': 'portateis_cozinha_e_preparadores_de_alimentos', 'product_category_name_english': 'portable_kitchen_food_processors'},
        {'product_category_name': 'tablets_impressao_imagem', 'product_category_name_english': 'tablets_printing_image'}
    ])
    
    # Agregar solo las que no existen ya
    categorias_existentes = set(df['product_category_name'].unique())
    nuevas_a_agregar = nuevas_traducciones[~nuevas_traducciones['product_category_name'].isin(categorias_existentes)]
    
    if len(nuevas_a_agregar) > 0:
        df = pd.concat([df, nuevas_a_agregar], ignore_index=True)
    
    # Limpiar columnas innecesarias
    df = df.drop('noise_flag', axis=1, errors='ignore')
    
    return df


# -----------------------
# Main
# -----------------------
def main():
    print("Starting CLEAN pipeline")

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    # Diccionario para guardar IDs válidos entre iteraciones
    valid_ids = {}

    pipelines = [
        ("customers", "olist_customers_dataset_dirty.csv", clean_customers),
        ("products", "olist_products_dataset_dirty.csv", clean_products),
        ("sellers", "olist_sellers_dataset_dirty.csv", clean_sellers),
        ("categories", "product_category_name_translation_dirty.csv", clean_category_translation),
        ("geolocation", "olist_geolocation_dataset_dirty.csv", clean_geolocation),
        ("orders", "olist_orders_dataset_dirty.csv", clean_orders),
        ("order_items", "olist_order_items_dataset_dirty.csv", clean_order_items),
        ("payments", "olist_order_payments_dataset_dirty.csv", clean_payments),
        ("reviews", "olist_order_reviews_dataset_dirty.csv", clean_reviews),
    ]

    for name, file, func in pipelines:
        df = load_csv(file)
        print(f"{name} loaded:", df.shape)

        # Pasar valid_ids según la función
        if name == "orders":
            df_clean = func(df, valid_ids.get('customer_id'))
        elif name == "order_items":
            df_clean = func(df, valid_ids.get('order_id'), valid_ids.get('product_id'), valid_ids.get('seller_id'))
        elif name in ["payments", "reviews"]:
            df_clean = func(df, valid_ids.get('order_id'))
        else:
            df_clean = func(df)
        
        print(f"{name} cleaned:", df_clean.shape)

        # Guardar IDs válidos para las siguientes tablas
        if name == "customers" and 'customer_id' in df_clean.columns:
            valid_ids['customer_id'] = set(df_clean['customer_id'].unique())
        elif name == "orders" and 'order_id' in df_clean.columns:
            valid_ids['order_id'] = set(df_clean['order_id'].unique())
        elif name == "products" and 'product_id' in df_clean.columns:
            valid_ids['product_id'] = set(df_clean['product_id'].unique())
        elif name == "sellers" and 'seller_id' in df_clean.columns:
            valid_ids['seller_id'] = set(df_clean['seller_id'].unique())

        df_clean.to_csv(
            CLEAN_DIR / f"{name}_clean.csv",
            index=False,
            date_format="%Y-%m-%d %H:%M:%S"
        )
        print(f"{name} CLEAN saved")

    print("CLEAN pipeline finished")


if __name__ == "__main__":
    main()
