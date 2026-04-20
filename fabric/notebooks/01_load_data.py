# Fabric Notebook: Load StreamFlow Demo Data
# ============================================
# Ce notebook charge les fichiers CSV générés dans le Lakehouse
# À exécuter dans un notebook Fabric connecté au Lakehouse lh_streamflow

# %% [markdown]
# # 📊 Chargement des données StreamFlow
# 
# Ce notebook charge les 9 tables de données (5 dimensions + 4 facts) dans le Lakehouse.

# %%
# Configuration
LAKEHOUSE_PATH = "Files/raw"  # Dossier où uploader les CSV d'abord

# Liste des tables
DIMENSION_TABLES = [
    "dim_date",
    "dim_geography", 
    "dim_offer",
    "dim_content",
    "dim_customer"
]

FACT_TABLES = [
    "fact_subscriptions",
    "fact_content_views",
    "fact_marketing",
    "fact_surveys"
]

ALL_TABLES = DIMENSION_TABLES + FACT_TABLES

# %% [markdown]
# ## Option 1 : Charger depuis les fichiers uploadés
# Si vous avez déjà uploadé les CSV dans Files/raw

# %%
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Charger chaque CSV et créer une table Delta
for table_name in ALL_TABLES:
    print(f"Loading {table_name}...")
    
    # Lire le CSV
    df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(f"Files/raw/{table_name}.csv")
    
    # Écrire en tant que table Delta
    df.write.format("delta") \
        .mode("overwrite") \
        .saveAsTable(table_name)
    
    print(f"  ✅ {table_name}: {df.count()} rows")

print("\n🎉 Toutes les tables ont été chargées!")

# %% [markdown]
# ## Option 2 : Générer les données directement dans le notebook
# Si vous n'avez pas les CSV, ce code génère les données directement

# %%
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
CONFIG = {
    'start_date': datetime(2024, 1, 1),
    'end_date': datetime(2025, 12, 31),
    'num_customers': 50000
}

# %% [markdown]
# ### Générer dim_date

# %%
def generate_dim_date():
    dates = pd.date_range(start=CONFIG['start_date'], end=CONFIG['end_date'], freq='D')
    return pd.DataFrame({
        'date_key': [int(d.strftime('%Y%m%d')) for d in dates],
        'date': dates,
        'year': dates.year,
        'month': dates.month,
        'month_name': dates.strftime('%B'),
        'quarter': dates.quarter,
        'week': dates.isocalendar().week,
        'day_of_week': dates.dayofweek,
        'day_name': dates.strftime('%A'),
        'is_weekend': dates.dayofweek >= 5
    })

dim_date = spark.createDataFrame(generate_dim_date())
dim_date.write.format("delta").mode("overwrite").saveAsTable("dim_date")
print(f"✅ dim_date: {dim_date.count()} rows")

# %% [markdown]
# ### Générer dim_geography

# %%
def generate_dim_geography():
    return pd.DataFrame({
        'geo_key': [1, 2, 3, 4, 5],
        'region': ['Europe', 'North America', 'Africa', 'Asia Pacific', 'Latin America'],
        'market_type': ['Mature', 'Mature', 'Emerging', 'Mixed', 'Emerging'],
        'currency': ['EUR', 'USD', 'EUR', 'USD', 'USD'],
        'market_weight': [0.35, 0.30, 0.15, 0.12, 0.08]
    })

dim_geography = spark.createDataFrame(generate_dim_geography())
dim_geography.write.format("delta").mode("overwrite").saveAsTable("dim_geography")
print(f"✅ dim_geography: {dim_geography.count()} rows")

# %% [markdown]
# ### Générer dim_offer

# %%
def generate_dim_offer():
    return pd.DataFrame({
        'offer_key': [1, 2, 3, 4],
        'offer_name': ['Basic', 'Standard', 'Premium', 'Family'],
        'monthly_price': [7.99, 12.99, 19.99, 24.99],
        'max_screens': [1, 2, 4, 6],
        'hd_available': [False, True, True, True],
        '4k_available': [False, False, True, True],
        'offer_weight': [0.25, 0.35, 0.30, 0.10]
    })

dim_offer = spark.createDataFrame(generate_dim_offer())
dim_offer.write.format("delta").mode("overwrite").saveAsTable("dim_offer")
print(f"✅ dim_offer: {dim_offer.count()} rows")

# %% [markdown]
# ### Vérifier les tables créées

# %%
# Afficher toutes les tables
spark.sql("SHOW TABLES").show()

# Aperçu de chaque table
for table in ["dim_date", "dim_geography", "dim_offer"]:
    print(f"\n--- {table} ---")
    spark.table(table).show(5)

# %% [markdown]
# ## 🎉 Données chargées!
# 
# Les tables sont maintenant disponibles dans le Lakehouse.
# Prochaine étape: Créer le Semantic Model dans Fabric.
