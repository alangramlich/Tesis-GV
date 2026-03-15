# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 14:48:17 2025

@author: alang
"""

# -*- coding: utf-8 -*-
"""
Adaptado para aplicar RandomUndersampling a múltiples archivos Excel
"""

import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
import matplotlib.pyplot as plt
import os

# Lista de archivos a procesar
archivos = [
    "dataset1_filtrado_buffer.xlsx",
    "dataset2_filtrado_buffer.xlsx",
    "dataset3_filtrado_buffer.xlsx",
    "dataset4_filtrado_buffer.xlsx",
    "dataset5_filtrado_buffer.xlsx",
    "dataset6_filtrado_buffer.xlsx",
]

for archivo in archivos:
    print(f"📂 Procesando archivo: {archivo}")
    
    # Leer todas las hojas excepto "Hoja1"
    excel = pd.ExcelFile(archivo)
    df_list = []
    for hoja in excel.sheet_names:
        if hoja != "Hoja1":
            df = pd.read_excel(archivo, sheet_name=hoja)
            df["origen"] = hoja
            df_list.append(df)

    if not df_list:
        print(f"⚠️ No se encontraron hojas útiles en {archivo}")
        continue

    df_full = pd.concat(df_list, ignore_index=True)

    # Separar características y etiquetas
    X = df_full.drop(columns=["clasificacion", "origen"])
    y = df_full["clasificacion"]

    # Aplicar RandomUndersampler
    rus = RandomUnderSampler(random_state=42)
    X_resampled, y_resampled = rus.fit_resample(X, y)

    # Guardar resultado
    df_under = X_resampled.copy()
    df_under["clasificacion"] = y_resampled

    nombre_salida = archivo.replace(".xlsx", "_undersampled.xlsx")
    df_under.to_excel(nombre_salida, index=False)
    print(f"✅ Archivo guardado como: {nombre_salida}")

    # Mostrar histograma
    y_resampled.value_counts().plot(kind="bar", color=["steelblue", "darkorange"])
    plt.title(f"Distribución de clases tras Undersampling ({os.path.basename(archivo)})")
    plt.xlabel("Clase")
    plt.ylabel("Cantidad de ventanas")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()
