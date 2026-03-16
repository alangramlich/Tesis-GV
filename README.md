# Proyecto de tesis

Este repositorio esta organizado para que sea facil ubicar que hace cada grupo de scripts y en que orden correrlos.

## Estructura del proyecto

- Datos crudos:
  - `siena-scalp-eeg-database-1.0.0`
  - `PlosONE_Data`
- Preprocesamiento:
  - [`preprocesamiento y transformaciones`](./preprocesamiento%20y%20transformaciones-20260315T153830Z-1-001/preprocesamiento%20y%20transformaciones)
- Datasets y variantes:
  - [`datasets`](./datasets-20260315T155725Z-1-001/datasets)
- Entrenamiento y visualizacion:
  - [`entrenamiento de modelos`](./entrenamiento%20de%20modelos-20260315T153853Z-1-001/entrenamiento%20de%20modelos)

## Requisitos

Antes de correr los scripts, instalar las dependencias de Python desde la raiz del repositorio:

```bash
pip install -r requirements.txt
```

Si se usa un entorno virtual, activarlo antes de correr ese comando.

## Orden de ejecucion

### Paso 1. Preprocesamiento inicial

En la carpeta `preprocesamiento y transformaciones`:

1. Correr `crear_dataset_csv.py`
2. Luego correr todos los scripts `agregar_*.py`

Esta etapa arma el archivo base de trabajo en Excel a partir de los EDF.

### Paso 2. Generacion de datasets y variantes

En la carpeta `datasets` podes seguir distintos flujos segun el tipo de dataset que quieras usar:

- Base:
  - usar los archivos de `datasets 1-6`
- Sin buffer:
  - correr `datasets 1 - 6 sin buffer/quitar_buffer.py`
- Con SMOTE:
  - correr `datasets 1 - 6 SMOTE/aplicar_smote.py`
- Con undersampling:
  - correr `datasets 1 - 6 undersampling/aplicar_undersampling.py`
- Sin buffer + SMOTE:
  - correr `datasets 1-6 sin buffer SMOTE/aplicar_smote.py`
- Sin buffer + undersampling:
  - correr `datasets 1 - 6 sin buffer undersampling/aplicar_undersampling.py`

### Paso 3. Entrenamiento

En la carpeta `entrenamiento de modelos`:

1. Correr `Entrenamiento_definitivo_V2.py`
2. Opcionalmente, correr `dashboard_resultados.py`

`Entrenamiento_definitivo_V2.py` genera resultados y graficos dentro de la carpeta `Resultados`.

Para correr el dashboard con las dependencias instaladas desde `requirements.txt`:

```bash
streamlit run "entrenamiento de modelos-20260315T153853Z-1-001/entrenamiento de modelos/dashboard_resultados.py"
```

## Que hace cada script

### Preprocesamiento

- `crear_dataset_csv.py`
  - inicia el archivo base y genera la primera hoja del Excel de trabajo.
- `agregar_P...py`
  - procesan un EDF puntual o un bloque de crisis y agregan una hoja nueva al Excel de trabajo.

### Datasets y variantes

- `quitar_buffer.py`
  - genera versiones filtradas sin buffer y tambien archivos de control visual.
- `aplicar_smote.py`
  - genera datasets balanceados usando SMOTE.
- `aplicar_undersampling.py`
  - genera datasets balanceados usando undersampling.

### Entrenamiento

- `Entrenamiento_definitivo_V2.py`
  - entrena modelos Random Forest sobre una carpeta de archivos Excel y guarda metricas y graficos.

### Visualizacion

- `dashboard_resultados.py`
  - carga los resultados generados y permite compararlos.

## Flujos sugeridos

### Flujo base

`crear_dataset_csv.py` -> `agregar_*.py` -> `Entrenamiento_definitivo_V2.py`

### Flujo con sin buffer

`crear_dataset_csv.py` -> `agregar_*.py` -> `quitar_buffer.py` -> `Entrenamiento_definitivo_V2.py`

### Flujo con SMOTE

`crear_dataset_csv.py` -> `agregar_*.py` -> datasets base o `aplicar_smote.py` -> `Entrenamiento_definitivo_V2.py`

### Flujo con undersampling

`crear_dataset_csv.py` -> `agregar_*.py` -> datasets base o `aplicar_undersampling.py` -> `Entrenamiento_definitivo_V2.py`

### Flujo con sin buffer y balanceo

`crear_dataset_csv.py` -> `agregar_*.py` -> `quitar_buffer.py` -> `aplicar_smote.py` o `aplicar_undersampling.py` -> `Entrenamiento_definitivo_V2.py`

## Carpeta de resultados

- Los resultados de entrenamiento se guardan en `entrenamiento de modelos/Resultados`
- Los scripts de variantes generan nuevos archivos Excel en sus carpetas correspondientes
- `dashboard_resultados.py` se usa despues del entrenamiento para explorar esos resultados

## Licencia

El codigo de este repositorio se distribuye bajo la licencia MIT. Ver [LICENSE](./LICENSE).

Los datasets, archivos de datos y derivados pueden estar sujetos a sus propias licencias, terminos de uso o restricciones de distribucion. Revisar la documentacion y condiciones de cada fuente antes de reutilizarlos o redistribuirlos.
