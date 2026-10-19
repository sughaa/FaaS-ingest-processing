from flask import Flask, request, jsonify
import re
import unicodedata
from collections import Counter

app = Flask(__name__)

NUMERIC_FIELDS = ("edad", "ingresos")
CATEGORICAL_FIELDS = ("genero", "ciudad")


def normalizar_texto(valor):
    """Minúsculas, elimina acentos/caracteres especiales y normaliza espacios."""
    if valor is None:
        return None
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto or None


def convertir_numero(valor):
    """Convierte a número; valores vacíos, inválidos o negativos se consideran faltantes."""
    if valor is None or valor == "":
        return None
    try:
        numero = float(valor)
        if numero < 0:
            return None
        return int(numero) if numero.is_integer() else numero
    except (TypeError, ValueError):
        return None


def moda(valores):
    conteo = Counter(v for v in valores if v is not None)
    if not conteo:
        return "desconocido"
    max_frecuencia = max(conteo.values())
    # Desempate estable para resultados reproducibles.
    return sorted(k for k, v in conteo.items() if v == max_frecuencia)[0]


def limpiar_registros(registros):
    if not isinstance(registros, list) or not registros:
        raise ValueError("'registros' debe ser una lista no vacía.")
    if any(not isinstance(r, dict) for r in registros):
        raise ValueError("Cada elemento de 'registros' debe ser un objeto JSON.")

    datos = []
    for r in registros:
        datos.append({
            "edad": convertir_numero(r.get("edad")),
            "ingresos": convertir_numero(r.get("ingresos")),
            "genero": normalizar_texto(r.get("genero")),
            "ciudad": normalizar_texto(r.get("ciudad")),
        })

    # Imputación numérica por media calculada sobre los valores válidos del lote.
    for campo in NUMERIC_FIELDS:
        valores = [r[campo] for r in datos if r[campo] is not None]
        if not valores:
            raise ValueError(
                f"No hay valores numéricos válidos para calcular la media de '{campo}'."
            )
        media = sum(valores) / len(valores)
        for r in datos:
            if r[campo] is None:
                r[campo] = round(media, 2)

    # Imputación categórica por moda calculada sobre los valores válidos del lote.
    for campo in CATEGORICAL_FIELDS:
        valor_moda = moda([r[campo] for r in datos])
        for r in datos:
            if r[campo] is None:
                r[campo] = valor_moda

    # One-Hot: categorías derivadas del lote recibido. En producción conviene fijar
    # el esquema con categorías aprendidas del conjunto de entrenamiento.
    categorias = {
        campo: sorted({r[campo] for r in datos})
        for campo in CATEGORICAL_FIELDS
    }

    salida = []
    for r in datos:
        fila = {"edad": r["edad"], "ingresos": r["ingresos"]}
        for campo in CATEGORICAL_FIELDS:
            for categoria in categorias[campo]:
                fila[f"{campo}_{categoria}"] = int(r[campo] == categoria)
        salida.append(fila)

    return {
        "columnas": list(salida[0].keys()),
        "total_registros": len(salida),
        "datos_transformados": salida,
    }


@app.get("/")
def inicio():
    return jsonify({
        "servicio": "API de limpieza y transformación para minería de datos",
        "estado": "activo",
        "endpoint": "POST /api/limpieza_datos"
    })


@app.post("/api/limpieza_datos")
def endpoint_limpieza():
    cuerpo = request.get_json(silent=True)
    if not isinstance(cuerpo, dict):
        return jsonify({"error": "Envía un objeto JSON válido en el cuerpo."}), 400
    try:
        resultado = limpiar_registros(cuerpo.get("registros"))
        return jsonify(resultado), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    # Solo para ejecución local. Render utiliza Gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=False)
