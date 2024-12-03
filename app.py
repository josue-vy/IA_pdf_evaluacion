from flask import Flask, request, jsonify
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import base64
import io
import numpy as np

# Inicializar Flask con el provider personalizado
app = Flask(__name__)

app.json.ensure_ascii = False

# Cargar el modelo preentrenado de Sentence-BERT
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Modelo ligero de Sentence-BERT

# Función para extraer texto de un PDF de CV
def extract_text_from_cv_pdf(pdf_bytes):

    text = ""
    # Convertir bytes a BytesIO
    pdf_stream = io.BytesIO(pdf_bytes)
    with pdfplumber.open(pdf_stream) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Función para calcular la similitud entre dos oraciones utilizando Sentence-BERT
def calcular_similitud_oracion(cv_oracion, requisito_oracion):
    # Obtener los embeddings de las oraciones
    embeddings_cv = model.encode([cv_oracion])
    embeddings_requisito = model.encode([requisito_oracion])

    # Calcular la similitud de coseno entre los embeddings
    similarity = cosine_similarity(embeddings_cv, embeddings_requisito)[0][0]
    return similarity

# Función para verificar si una oración del requisito está exactamente en el CV
def encontrar_coincidencia_exacta(cv_text, requisito_oracion):
    # Limpiar el texto del CV y del requisito de caracteres especiales como puntos y comas
    cv_text = re.sub(r'\s+', ' ', cv_text.strip())  # Quitar saltos de línea extra
    requisito_oracion = re.sub(r'\s+', ' ', requisito_oracion.strip())  # Quitar saltos de línea extra

    # Verificar si el requisito (oración) está exactamente en el CV
    return requisito_oracion.lower() in cv_text.lower()

# Función para calcular el puntaje de similitud entre el CV y los requisitos
def calcular_puntaje_cv(cv_text, requisitos):
    # Contar el total de sub-requisitos
    total_sub_requisitos = sum(len(lista_req) for lista_req in requisitos.values())
    print(f"Total de sub-requisitos: {total_sub_requisitos}")
    
    puntaje_total = 0
    oraciones_similares = []

    # Dividir el texto del CV en oraciones
    oraciones_cv = cv_text.split('\n')

    # Valor por cada sub-requisito cumplido
    valor_por_requisito = 100 / total_sub_requisitos if total_sub_requisitos > 0 else 0
    print(f"Valor por cada requisito cumplido: {valor_por_requisito}%")

    # Comprobar cada categoría
    for categoria, lista_requisitos in requisitos.items():
        print(f"\nEvaluando categoría: {categoria}")
        print(f"Número de sub-requisitos en {categoria}: {len(lista_requisitos)}")
        
        for requisito in lista_requisitos:
            # Verificar coincidencia exacta
            if encontrar_coincidencia_exacta(cv_text, requisito):
                oraciones_similares.append((requisito, "Coincidencia exacta", 100))
                puntaje_total += valor_por_requisito
                print(f"Coincidencia exacta encontrada: {requisito}")
                print(f"Puntaje acumulado: {puntaje_total}%")
            else:
                # Buscar coincidencia por similitud
                mejor_similitud = 0
                mejor_oracion = None
                
                for oracion_cv in oraciones_cv:
                    similitud = calcular_similitud_oracion(oracion_cv, requisito)
                    if similitud > 0.8 and similitud > mejor_similitud:
                        mejor_similitud = similitud
                        mejor_oracion = oracion_cv

                if mejor_oracion:
                    similitud_porcentaje = mejor_similitud * 100
                    puntaje_parcial = valor_por_requisito * (mejor_similitud)
                    puntaje_total += puntaje_parcial
                    oraciones_similares.append((mejor_oracion, requisito, similitud_porcentaje))
                    print(f"Similitud encontrada: {requisito}")
                    print(f"Porcentaje de similitud: {similitud_porcentaje}%")
                    print(f"Puntaje acumulado: {puntaje_total}%")

    print(f"\nPuntaje final total: {puntaje_total}%")
    return puntaje_total, oraciones_similares


@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
    try:
        # Obtener datos del request
        data = request.json
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400

        # Validar campos requeridos
        if 'cv_pdf_base64' not in data or 'requisitos' not in data:
            return jsonify({
                "error": "Faltan campos requeridos. Se necesita 'cv_pdf_base64' y 'requisitos'"
            }), 400

        # Decodificar el PDF
        try:
            pdf_bytes = base64.b64decode(data['cv_pdf_base64'])
            print("PDF decodificado correctamente")
        except Exception as e:
            print(f"Error en decodificación base64: {str(e)}")
            return jsonify({"error": f"Error al decodificar el PDF: {str(e)}"}), 400

        # Extraer texto del PDF
        try:
            cv_text = extract_text_from_cv_pdf(pdf_bytes)
            print("Texto extraído correctamente del PDF")
        except Exception as e:
            print(f"Error en extracción de texto: {str(e)}")
            return jsonify({"error": f"Error al procesar el PDF: {str(e)}"}), 400

        # Calcular similitud
        try:
            puntaje_similitud, oraciones_similares = calcular_puntaje_cv(cv_text, data['requisitos'])

            # Asegurar que los valores son tipos nativos de Python
            puntaje_similitud = float(puntaje_similitud)
            oraciones_similares = [
                (str(o[0]), str(o[1]), float(o[2])) 
                for o in oraciones_similares
            ]

            resultado = {
                'puntaje_total': puntaje_similitud,
                'coincidencias': oraciones_similares
            }

            print("Tipo de puntaje_total:", type(puntaje_similitud))
            print("Tipo de coincidencias:", type(oraciones_similares))
            print("Resultado:", resultado)

            return jsonify(resultado)

        except Exception as e:
            print(f"Error en el cálculo de similitud: {str(e)}")
            return jsonify({"error": f"Error en el cálculo de similitud: {str(e)}"}), 500

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        print(f"Tipo del error: {type(e)}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


if __name__ == '__main__':
    app.run()