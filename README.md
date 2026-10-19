# API de limpieza para minería de datos (Render)

## Qué hace
- Recibe JSON por `POST /api/limpieza_datos`.
- Normaliza texto: minúsculas, elimina acentos y caracteres especiales.
- Imputa `edad` e `ingresos` con la media de valores válidos del lote.
- Imputa `genero` y `ciudad` con la moda.
- Codifica las categorías mediante One-Hot Encoding (columnas 0/1).

## Desplegar en Render
1. Sube estos archivos a un repositorio de GitHub.
2. En https://render.com/, inicia sesión y selecciona **New +** → **Web Service**.
3. Conecta el repositorio de GitHub.
4. Configura:
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free, si aparece disponible para tu cuenta/región.
5. Haz clic en **Create Web Service** y espera el despliegue.
6. La URL pública será similar a `https://nombre-del-servicio.onrender.com`.
7. Comprueba la raíz `https://nombre-del-servicio.onrender.com/`.
8. Envía el JSON de `request.json` por POST a:
   `https://nombre-del-servicio.onrender.com/api/limpieza_datos`

## Probar con curl
```bash
curl -X POST "https://TU-SERVICIO.onrender.com/api/limpieza_datos" \
  -H "Content-Type: application/json" \
  --data @request.json
```

## Importante
- El plan gratuito puede suspender servicios inactivos y tiene límites que Render puede cambiar.
- Esta aplicación es una API web, no una función serverless nativa como Azure Functions.
- La imputación y las categorías se calculan con cada lote recibido. Para producción/modelos predictivos, calcula estos parámetros en entrenamiento y reutilízalos después.
- Usa datos ficticios, no información personal sensible.
