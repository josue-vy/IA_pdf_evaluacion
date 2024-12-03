import requests
import base64

# Leer el PDF y convertirlo a base64
with open("Branco_Conislla.pdf", "rb") as pdf_file:
    pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')

data = {
    "cv_pdf_base64": pdf_base64,
    "requisitos": {
        "formacion_academica": [
        "Titulado Profesional Técnico en Computacion e Informática",
        "Bachiller en ciencias con mención en Ingeniería Química",
        "Licenciatura en Ciencias de la Computación",
        "Máster en Ingeniería de Sistemas"
        ],
        "ofimatica": [
            "Microsoft Power Point Nivel Avanzado", "Microsoft Excel Nivel Avanzado",
            "Microsoft Word Nivel Avanzado"
        ],
        "lenguajes_idiomas": [
            "Ingles", "Español"
        ],
        "experiencia": [
            "Un 01 año de experiencia en soporte a usuarios de sistemas de información",
            "Un 01 año como auxiliar o asistente"
        ]
    }

}

try:
    # Hacer la solicitud POST
    response = requests.post(
        "http://localhost:5000/calculate_similarity",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()  # Levanta una excepción si el status code es >= 400
    resultado = response.json()
    print(resultado)
except requests.exceptions.RequestException as e:
    print(f"Error en la solicitud: {e}")