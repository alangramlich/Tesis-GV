import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")
st.title("📊 Comparador de resultados Random Forest")

# === Cargar todos los archivos Excel ===
@st.cache_data
def cargar_datasets(carpeta_base):
    todos_dfs = []
    for root, _, files in os.walk(carpeta_base):
        for file in files:
            if file.endswith(".xlsx") and "resultados_" in file:
                path = os.path.join(root, file)
                try:
                    df = pd.read_excel(path)
                    df["archivo"] = os.path.splitext(file)[0]
                    todos_dfs.append(df)
                except Exception as e:
                    st.warning(f"No se pudo leer {file}: {e}")
    if not todos_dfs:
        return pd.DataFrame()
    return pd.concat(todos_dfs, ignore_index=True)

# === Cargar datos ===
carpeta_resultados = "C:/Users/alang/OneDrive/Desktop/Entrenar IA Tesis/Resultados"
df = cargar_datasets(carpeta_resultados)

if df.empty:
    st.error("❌ No se encontraron archivos de resultados.")
    st.stop()

# === Filtros ===
datasets = df["archivo"].unique()
max_depths = df["max_depth"].astype(str).unique()
train_pcts = df["Train %"].unique()
metricas = ["Accuracy", "Precisión preictal", "Recall preictal", "F1 preictal"]

col1, col2, col3 = st.columns(3)
with col1:
    datasets_sel = st.multiselect("📁 Datasets", datasets, default=list(datasets))
with col2:
    depth_sel = st.multiselect("🌲 max_depth", sorted(max_depths), default=sorted(max_depths))
with col3:
    train_sel = st.multiselect("🎓 % Entrenamiento", sorted(train_pcts), default=sorted(train_pcts))

df_filtrado = df[
    (df["archivo"].isin(datasets_sel)) &
    (df["max_depth"].astype(str).isin(depth_sel)) &
    (df["Train %"].isin(train_sel))
]

# === Mostrar tabla ===
st.subheader("📋 Resultados filtrados")
st.dataframe(df_filtrado)

# === Seleccionar métrica a graficar ===
metrica = st.selectbox("📈 Métrica a graficar", metricas)

# === Gráfico comparativo ===
st.subheader("📊 Comparación de métricas por Dataset")
fig, ax = plt.subplots(figsize=(12, 6))
for archivo in datasets_sel:
    df_sub = df_filtrado[df_filtrado["archivo"] == archivo]
    ax.plot(
        df_sub["Train %"],
        df_sub[metrica],
        label=archivo,
        marker="o"
    )
ax.set_title(f"{metrica} vs % Entrenamiento")
ax.set_xlabel("% Entrenamiento")
ax.set_ylabel(metrica)
ax.legend()
ax.grid(True)
# Mostrar el gráfico principal sin leyenda
handles, labels = ax.get_legend_handles_labels()
ax.get_legend().remove()  # Quitar leyenda del gráfico principal
st.pyplot(fig)

# Mostrar la leyenda como imagen separada
fig_legend = plt.figure(figsize=(6, 1.5))
fig_legend.legend(handles, labels, loc='center', ncol=len(labels), frameon=False)
plt.axis('off')
st.pyplot(fig_legend)

