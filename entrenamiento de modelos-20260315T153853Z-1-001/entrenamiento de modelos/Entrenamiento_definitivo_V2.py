import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog

# === Configuración general ===
caracteristicas = ['nni_diff_mean', 'CSI', 'hr_std', 'HF_power', 'SampEn', 'pnn50']
columna_etiquetas = "clasificacion"
directorio_script = os.path.dirname(os.path.abspath(__file__))
directorio_resultados_general = os.path.join(directorio_script, "Resultados")

# Crear carpeta base de resultados si no existe
os.makedirs(directorio_resultados_general, exist_ok=True)

# === Selección de carpeta raíz ===
tk.Tk().withdraw()
carpeta_raiz = filedialog.askdirectory(title="Selecciona la carpeta que contiene los archivos Excel")
if not carpeta_raiz:
    print("❌ No se seleccionó ninguna carpeta. Saliendo...")
    exit()

# === Buscar archivos Excel, ignorando carpetas con "control" ===
extensiones_validas = ('.xlsx', '.xls')
archivos_excel = []

for carpeta_actual, _, archivos in os.walk(carpeta_raiz):
    if "control" in carpeta_actual.lower():
        continue  # Ignorar carpetas con "control"

    for archivo in archivos:
        if archivo.lower().endswith(extensiones_validas):
            ruta_completa = os.path.join(carpeta_actual, archivo)
            archivos_excel.append(ruta_completa)

if not archivos_excel:
    print("⚠️ No se encontraron archivos Excel válidos.")
    exit()

print(f"\n🔍 Se encontraron {len(archivos_excel)} archivos Excel para procesar.\n")

# === Procesar cada archivo ===
for archivo in archivos_excel:
    try:
        nombre_archivo = os.path.basename(archivo)
        base_nombre_archivo = os.path.splitext(nombre_archivo)[0]

        # Obtener subcarpeta relativa y normalizar para nombres válidos
        subcarpeta_relativa = os.path.relpath(os.path.dirname(archivo), carpeta_raiz).replace("\\", "_").replace("/", "_")
        base_nombre_unico = f"{subcarpeta_relativa}_{base_nombre_archivo}"

        # Crear subcarpeta de resultados específica
        subcarpeta_resultado = os.path.join(directorio_resultados_general, subcarpeta_relativa)
        os.makedirs(subcarpeta_resultado, exist_ok=True)

        print(f"\n📁 Procesando: {nombre_archivo} (origen: {subcarpeta_relativa})")

        xls = pd.ExcelFile(archivo)
        df_list = []

        for hoja in xls.sheet_names:
            df_hoja = pd.read_excel(xls, sheet_name=hoja)

            if not all(col in df_hoja.columns for col in caracteristicas + [columna_etiquetas]):
                continue

            y_tmp = df_hoja[columna_etiquetas]
            conteo = y_tmp.value_counts()

            if conteo.get("preictal", 0) >= 2 and conteo.get("no_preictal", 0) >= 2:
                df_hoja["__origen"] = hoja
                df_list.append(df_hoja)

        if not df_list:
            print(f"🚫 Sin hojas válidas (menos de 2 muestras por clase).")
            continue

        df = pd.concat(df_list, ignore_index=True)
        X = df[caracteristicas]
        y = df[columna_etiquetas]

        porcentajes_entrenamiento = [0.70, 0.75, 0.80, 0.85, 0.90]
        profundidades = [5, 10, 15, 20, None]
        resultados = []

        for train_size in porcentajes_entrenamiento:
            resto = 1 - train_size
            val_size = resto / 2
            test_size = resto / 2

            try:
                X_train, X_temp, y_train, y_temp = train_test_split(X, y, train_size=train_size, stratify=y, random_state=42)
                X_test, X_val, y_test, y_val = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)
            except ValueError as e:
                print(f"⚠️ Error con train_size={train_size}: {e}")
                continue

            for depth in profundidades:
                modelo = RandomForestClassifier(n_estimators=100, max_depth=depth, random_state=42)
                modelo.fit(X_train, y_train)
                y_pred = modelo.predict(X_test)

                reporte = classification_report(y_test, y_pred, labels=["no_preictal", "preictal"], output_dict=True, zero_division=0)
                accuracy = accuracy_score(y_test, y_pred)

                resultados.append({
                    "Train %": train_size,
                    "Test %": test_size,
                    "Validación %": val_size,
                    "max_depth": str(depth) if depth is not None else "None",
                    "Accuracy": round(accuracy, 4),
                    "Precisión preictal": round(reporte['preictal']['precision'], 4),
                    "Recall preictal": round(reporte['preictal']['recall'], 4),
                    "F1 preictal": round(reporte['preictal']['f1-score'], 4)
                })

        if not resultados:
            print("⚠️ No se generaron resultados.")
            continue

        df_resultados = pd.DataFrame(resultados)
        path_excel = os.path.join(subcarpeta_resultado, f"resultados_{base_nombre_unico}.xlsx")
        df_resultados.to_excel(path_excel, index=False)
        print(f"✅ Resultados guardados: {path_excel}")

        # === Graficar y guardar imágenes ===
        orden_depth = ["5", "10", "15", "20", "None"]
        df_resultados["max_depth"] = pd.Categorical(df_resultados["max_depth"], categories=orden_depth, ordered=True)

        # Gráfico 1
        depth_summary = df_resultados.groupby("max_depth", observed=True)[["Accuracy", "Precisión preictal", "Recall preictal", "F1 preictal"]].mean().reset_index()
        depth_melted = depth_summary.melt(id_vars="max_depth", var_name="Métrica", value_name="Valor")

        plt.figure(figsize=(12, 6))
        sns.barplot(data=depth_melted, x="max_depth", y="Valor", hue="Métrica", order=orden_depth)
        plt.title(f"Métricas promedio por profundidad\n{base_nombre_unico}")
        plt.ylabel("Valor promedio")
        plt.xlabel("Profundidad máxima")
        plt.legend(title="Métrica")
        plt.tight_layout()
        path_grafico1 = os.path.join(subcarpeta_resultado, f"grafico_max_depth_{base_nombre_unico}.png")
        plt.savefig(path_grafico1)
        plt.close()

        # Gráfico 2
        train_summary = df_resultados.groupby("Train %")[["Accuracy", "Precisión preictal", "Recall preictal", "F1 preictal"]].mean().reset_index()
        train_melted = train_summary.melt(id_vars="Train %", var_name="Métrica", value_name="Valor")

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=train_melted, x="Train %", y="Valor", hue="Métrica", marker="o")
        plt.title(f"Evolución de métricas por % entrenamiento\n{base_nombre_unico}")
        plt.ylabel("Valor promedio")
        plt.xlabel("% de entrenamiento")
        plt.grid(True)
        plt.tight_layout()
        path_grafico2 = os.path.join(subcarpeta_resultado, f"grafico_train_split_{base_nombre_unico}.png")
        plt.savefig(path_grafico2)
        plt.close()

        print(f"🖼️ Gráficos guardados:\n  - {path_grafico1}\n  - {path_grafico2}")

    except Exception as e:
        print(f"❌ Error al procesar {archivo}:\n{e}")
