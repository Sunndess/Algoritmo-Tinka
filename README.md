# Predicción de Jugadas Tinka con Machine Learning

Este proyecto automatiza la obtención de resultados históricos de la **Tinka Perú** directamente desde la web oficial de Tinka Resultados y utiliza **Machine Learning (Random Forest)** para predecir los números más probables de la próxima jugada.

## 🚀 Funcionalidades principales
- **Scraping automático**: descarga los resultados de cada sorteo (miércoles y domingos) desde la web.
- **Caché local**: guarda el dataset en la carpeta `Historial/tinka_dataset.xlsx` y evita volver a scrapear si ya está actualizado el mismo día.
- **Normalización de datos**: asegura que todas las columnas estén presentes y con formato correcto.
- **Features avanzadas para ML**:
  - Día de la semana, mes, año.
  - Número de ganadores y premios.
  - Frecuencia global de aparición de cada número.
  - Recencia (días desde la última aparición).
  - Impacto de premios mayores (6 aciertos).
- **Entrenamiento del modelo**: usa un `RandomForestClassifier` con múltiples features para aprender patrones históricos.
- **Predicción automática**:
  - Muestra la **última fecha tomada** para la predicción.
  - Calcula los **6 números recomendados**.
  - Sugiere el **Boliyapa**.

## 📂 Estructura del proyecto
- `import requests.txt` → Script principal (puedes renombrarlo como `tinka_prediccion.py`).
- `Historial/tinka_dataset.xlsx` → Dataset actualizado con los resultados históricos.

## ⚙️ Requisitos
- Python 3.8+
- Librerías:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `numpy`
  - `scikit-learn`
  - `openpyxl`

Instalación rápida:
```bash
pip install requests beautifulsoup4 pandas numpy scikit-learn openpyxl
