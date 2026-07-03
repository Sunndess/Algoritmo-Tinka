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
```

## ▶️ Cómo ejecutarlo

Backend local con Flask:
```bash
python app.py
```

Luego abre `http://127.0.0.1:5000/`.

## 🌐 GitHub Pages

GitHub Pages solo puede servir el frontend estático. Para que los botones `Actualizar`, `Predecir` y `Descargar Dataset` funcionen, necesitas desplegar `app.py` en otro servicio, por ejemplo Render, Railway o un VPS, y luego definir `window.API_BASE_URL` con la URL pública de esa API.

Ejemplo en `index.html`:
```html
<script>
  window.API_BASE_URL = 'https://tu-backend.onrender.com';
</script>
```

Si lo publicas solo en Pages sin backend, verás errores de conexión porque `/update` y `/predict` no existen allí.

## 🚀 Desplegar en Render

1. Sube el proyecto completo a un repositorio de GitHub.
2. En Render, crea un nuevo **Web Service** y conecta ese repositorio.
3. Render detectará Python; si usas `render.yaml`, tomará `buildCommand` y `startCommand` automáticamente.
4. La URL pública de tu backend será algo como `https://algoritmo-tinka.onrender.com`.
5. En tu frontend de GitHub Pages, define:
```html
<script>
  window.API_BASE_URL = 'https://algoritmo-tinka.onrender.com';
</script>
```

### Valores que debes usar en Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment: `Python`
- Port: Render lo asigna automáticamente; `app.py` ya lo toma desde la variable `PORT`.

### Importante
GitHub Pages no puede ejecutar Flask. Debes publicar el frontend estático en Pages y el backend en Render, o publicar todo en Render si quieres una sola URL.
