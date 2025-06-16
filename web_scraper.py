# Bibliotecas de Python usadas (toca descargarlas si no las tienes)
import os
import requests
import re
import json
from bs4 import BeautifulSoup
from difflib import get_close_matches
import ast

# === GLOBALES ===
# Ciudades a procesar
CIUDADES = ["Lorca"]

# Almacén de ciudades en la web. Las de aquí no se usan en la ejecución
CIUDADES_NO_USADAS = ["Almería", "Antequera", "Aranjuez", "Barcelona", "Bilbao", "Burgos", "Cartagena", "Cáceres", "Cuenca", "Don Benito", "Getafe", "Gijón", "Granada", 
                      "Leganés", "León", "Logroño", "Las Rozas de Madrid", "Madrid", "Marbella", "Melilla", "Oviedo", "Palma de Mallorca", "Pamplona", "Plasencia", 
                      "Puerto Real", "Reus", "Salamanca", "Santa Cruz de Tenerife", "Santander", "Sevilla", "Soria", "Talavera de la Reina", "Tomelloso", "Toledo", 
                      "Valencia", "Vigo", "Vitoria", "Zamora", "Zaragoza"]

#Características para Deepseek
DATOS = [
    "País",
    "Comunidad autónoma",
    "Provincia",
    "Número de habitantes",
    "Servicios de transporte público",
    "Limpieza, higiene y gestión de residuos",
    "Principales actividades económicas",
    "Estilo arquitectónico predominante o monumentos destacados",
    "Importancia histórica de la ciudad",
    "Nivel de turismo (lugares turísticos más visitados)",
    "Nivel educativo (universidades o centros de estudio relevantes)",
    "Calidad de vida",
    "Medio ambiente (zonas verdes, parques, contaminación)",
    "Seguridad y medidas de protección"
]

# Fuentes externas de información turística a ejecutar (una por ciudad)
TURISMO = { "Lorca": "https://lorcaturismo.es/situacion/situacion.asp?id=53&lang=es" }

# Almacén de fuentes extrenas (una por ciuda). Las de aquí no se procesan
TURISMO_NO_USADO = {
    "Almería": "https://www.andalucia.org/lugares-para-visitar/almeria/almeria/",
    "Antequera": "https://www.legadoandalusi.es/revista/antequera/",
    "Aranjuez": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-madrid/guia-de-aranjuez/",
    "Barcelona": "https://irbarcelona.com/informacion-ciudad-barcelona/",
    "Bilbao": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-vizcaya/guia-de-bilbao/",
    "Burgos": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-burgos/guia-de-burgos/",
    "Cartagena": "https://queverenelmundo.com/que-ver-en-espana/region-de-murcia/guia-de-cartagena/",
    "Cáceres": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-caceres/guia-de-caceres/",
    "Cuenca": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-cuenca/guia-de-cuenca/",
    "Don Benito": "https://www.dip-badajoz.es/municipios/municipio_dinamico/historia/index_historia.php?codigo=042",
    "Getafe": "https://www.verpueblos.com/comunidad+de+madrid/madrid/getafe/",
    "Gijón": "https://asturias.com/gijon-informacion-basica/?srsltid=AfmBOop1PZq3yY5IzJe6jCze_qIpwRPmAhBQj4gsOAExVCB1Hn_MBQIi",
    "Granada": "https://www.andalucia.org/lugares-para-visitar/granada/granada/",
    "Leganés": "https://www.verpueblos.com/comunidad+de+madrid/madrid/leganes/",
    "León": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-leon/guia-de-leon/",
    "Logroño": "https://lariojaturismo.com/poblacion/logroo/b7d10bba-9e65-4a1f-9209-69d736283607",
    "Las Rozas de Madrid": "https://www.verpueblos.com/comunidad+de+madrid/madrid/las+rozas/",
    "Madrid": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-madrid/guia-de-madrid/",
    "Marbella": "https://www.andalucia.org/listing/marbella/19912102/",
    "Melilla": "https://es.wikivoyage.org/wiki/Melilla",
    "Oviedo": "https://asturias.com/oviedo-informacion-basica/?srsltid=AfmBOooc1ZYkpm8qnHyauKXyEvhtWXX2mPwvvg4EJv5fWTT4cTwbs-RW",
    "Palma de Mallorca": "https://www.abc-mallorca.es/palma-de-mallorca/",
    "Pamplona": "https://queverenelmundo.com/que-ver-en-espana/comunidad-de-navarra/guia-de-pamplona/",
    "Plasencia": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-caceres/guia-de-plasencia/",
    "Puerto Real": "https://www.guiadecadiz.com/es/localidades/puerto-real",
    "Reus": "https://www.reus-tourist-guide.com/es/index.html",
    "Salamanca": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-salamanca/guia-de-salamanca/",
    "Santa Cruz de Tenerife": "https://wonderfultenerife.com/es/article/show/219/santa-cruz-de-tenerife",
    "Santander": "https://queverenelmundo.com/que-ver-en-espana/comunidad-de-cantabria/guia-de-santander/",
    "Sevilla": "https://www.andalucia.org/lugares-para-visitar/sevilla/sevilla/",
    "Soria": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-soria/guia-de-soria/",
    "Talavera de la Reina": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-toledo/talavera-de-la-reina/",
    "Tomelloso": "https://www.tomelloso.es/articulos/nuestra-ciudad",
    "Toledo": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-toledo/guia-de-toledo/",
    "Valencia": "https://www.valencia.es/cas/la-ciudad",
    "Vigo": "https://galicia.info/vigo/",
    "Vitoria": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-alava/vitoria-gasteiz/",
    "Zamora": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-zamora/guia-de-zamora/",
    "Zaragoza": "https://queverenelmundo.com/que-ver-en-espana/provincia-de-zaragoza/guia-de-zaragoza/"}

# Categorías como se presentan en el JSON y en la Web
CATEGORIAS = ["País", "Comunidad autónoma", "Provincia", "Número de habitantes", "Servicios de transporte público", "Limpieza", 
              "Actividades económicas", "Estilo arquitectónico", "Importancia histórica", "Nivel de turismo", "Nivel educativo", 
              "Calidad de vida", "Medio ambiente", "Seguridad"]

#Intento de localizar categorías sin datos
FALLOS  = ["No se proporciona", "No se especifica en el texto", "No se especifica en el texto proporcionado.", 
                         "", "No se especifican detalles en el texto proporcionado", "No disponible", 
                         "No se proporcionan detalles específicos en el texto.", "No especificado en el texto proporcionado", "Desconocido"]

# URLs y rutas de archivos
WIKIPEDIA = "https://es.wikipedia.org/wiki/"
WIKIS_DIR = "./wikis/"
TXT_OUTPUT_PATH = "./web/dbs/Gepeto/Gepeto_reviews.txt"
JSON_OUTPUT_PATH = "./web/dbs/Gepeto/Gepeto_reviews.json"
DEEPSEEK_URL = "http://0.0.0.0:11434/api/generate"
MODEL_BASE = "deepseek-r1:14b"
TURISMO_DIR = "./fuentes_turismo/"



# Crear directorios si no existen
os.makedirs(TURISMO_DIR, exist_ok=True)
os.makedirs(WIKIS_DIR, exist_ok=True)

#Cargar JSON existente si existe
def cargar_json_existente():
    if os.path.exists(JSON_OUTPUT_PATH):
        with open(JSON_OUTPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Función para limpiar las respuestas de Deepseek
def limpiar_respuesta(texto):
    return re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL).strip()

# Función que consulta Deepseek para extraer los datos
def ask_deepseek(prompt, model=MODEL_BASE):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(DEEPSEEK_URL, json=data)
    response.raise_for_status()
    return response.json()["response"]

# Función para obtener el texto de Wikipedia de una ciudad
def obtener_texto_wikipedia(ciudad):
    filename = os.path.join(WIKIS_DIR, f"{ciudad.replace(' ', '_')}.txt")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    print(f"Descargando artículo de Wikipedia para {ciudad}...")
    url = WIKIPEDIA + ciudad.replace(" ", "_")
    if ciudad == "Cartagena" or ciudad == "León":
        url += "_(España)"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        parrafos = soup.find_all("p")
        texto = "\n".join(p.get_text() for p in parrafos if p.get_text().strip())
        with open(filename, "w", encoding="utf-8") as f:
            f.write(texto)
        return texto
    except Exception as e:
        print(f"Error obteniendo texto para {ciudad}: {e}")
        return ""

# Función para obtener el texto de Turismo de una ciudad
def obtener_texto_turismo(ciudad):
    ruta = os.path.join(TURISMO_DIR, f"{ciudad.replace(' ', '_')}.txt")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()

    if ciudad not in TURISMO:
        return ""

    try:
        print(f"Descargando información externa para {ciudad}...")
        response = requests.get(TURISMO[ciudad])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        parrafos = soup.find_all("p")
        texto = "\n".join(p.get_text() for p in parrafos if p.get_text().strip())

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)
        return texto
    except Exception as e:
        print(f"Error turismo para {ciudad}: {e}")
        return ""

def generar_prompt_wikipedia(ciudad, texto, datos):
    prompt = f"""
Eres un asistente experto en ciudades y análisis de datos. Se te proporciona un texto parcial de Wikipedia sobre la ciudad de {ciudad}, además de tu conocimiento general como modelo de lenguaje.

Tu tarea es EXTRAER o INFERIR los siguientes datos, de forma clara, literal y concisa. Para cada uno:

- Si aparece explícitamente en el texto, transcribe o resume el dato.
- Si NO aparece, dedúcelo razonablemente con tu conocimiento sobre la ciudad.
- Si no puedes estar seguro, escribe: "Desconocido".
- No inventes datos falsos.
- Sé especialmente preciso y detallado con:
  → "Sistema de transporte público (metro, autobuses, trenes, etc.)"
  → "Limpieza y gestión de residuos"

Devuelve la respuesta en **formato JSON**, con las siguientes claves exactamente como están escritas:
"""
    for dato in datos:
        prompt += f'- {dato}\n'
    prompt += f"""

Texto de Wikipedia (incompleto, solo como referencia inicial):
\"\"\"{texto}\"\"\"

Formato de salida:
{{
  "País": "...",
  "Comunidad autónoma": "...",
  "Provincia": "...",
  "Número de habitantes": "...",
  "Servicios de transporte público": "...",
  "Limpieza, higiene y gestión de residuos": "...",
  "Principales actividades económicas": "...",
  "Estilo arquitectónico predominante o monumentos destacados": "...",
  "Importancia histórica de la ciudad": "...",
  "Nivel de turismo (lugares turísticos más visitados)": "...",
  "Nivel educativo (universidades o centros de estudio relevantes)": "...",
  "Calidad de vida": "...",
  "Medio ambiente (zonas verdes, parques, contaminación)": "...",
  "Seguridad y medidas de protección": "..."
}}
Devuelve SOLO el JSON. Nada más.
"""
    return prompt
def generar_prompt_otras_fuentes(ciudad, texto, datos):
    prompt = f"""
Eres un asistente experto en análisis de información sobre ciudades. A continuación, se te proporciona un texto relacionado con la ciudad de {ciudad}, que puede provenir de fuentes diversas (noticias, blogs, artículos, etc.).

TU OBJETIVO:
Intentar extraer o inferir la información correspondiente a las siguientes categorías. Sigue el orden propuesto lo mejor posible.

INSTRUCCIONES:
- Si el dato aparece claramente en el texto: extráelo.
- Si puede deducirse con razonable certeza: infiérelo.
- Si no se menciona o no es claro: escribe **"No disponible"**.
- Aunque algunas categorías no tengan datos, incluye todas en la salida final.
- El resultado debe presentarse en formato JSON.

Categorías sugeridas:
""" + "\n".join(f"- {d}" for d in datos) + f"""

Texto disponible:
\"\"\"{texto}\"\"\"

Formato de salida (JSON completo, incluso con "No disponible"):
{{
  "País": "...",
  "Comunidad autónoma": "...",
  "Provincia": "...",
  "Número de habitantes": "...",
  "Servicios de transporte público": "...",
  "Limpieza, higiene y gestión de residuos": "...",
  "Principales actividades económicas": "...",
  "Estilo arquitectónico predominante o monumentos destacados": "...",
  "Importancia histórica de la ciudad": "...",
  "Nivel de turismo (lugares turísticos más visitados)": "...",
  "Nivel educativo (universidades o centros de estudio relevantes)": "...",
  "Calidad de vida": "...",
  "Medio ambiente (zonas verdes, parques, contaminación)": "...",
  "Seguridad y medidas de protección": "..."
}}
"""
    return prompt

def check_type(datos):
    datos_estandarizados = {}
    claves = list(datos.keys())
    for categoria in CATEGORIAS:
        stop = False
        for clave in claves:
            if categoria.lower() in clave.lower():
                datos_estandarizados[categoria] = datos[clave]
                stop = True
                break
        if not stop:
            datos_estandarizados[categoria] = "No disponible"
            print(categoria, "X")
    return datos_estandarizados

# Función que recolecta los datos de Wikipedia
def recolectar_datos_wikipedia(tabla):
    for ciudad in CIUDADES:
        print(f"Procesando {ciudad} (Wikipedia)...")
        texto_wiki = obtener_texto_wikipedia(ciudad)

        if not texto_wiki.strip():
            continue

        prompt = generar_prompt_wikipedia(ciudad, texto_wiki, DATOS)
        respuesta = ask_deepseek(prompt)
        limpia = limpiar_respuesta(respuesta)

        datos_ciudad = {}
        try:
            datos_ciudad = json.loads(limpia)
        except json.JSONDecodeError:
            try:
                datos_ciudad = ast.literal_eval(limpia)
            except Exception:
                json_aprox = re.findall(r'"([^"]+)"\s*:\s*(.*?)(,|\n|$)', limpia)
                for clave, valor, _ in json_aprox:
                    match = get_close_matches(clave.strip(), DATOS, n=1, cutoff=0.4)
                    if match:
                        datos_ciudad[match[0]] = valor.strip().strip('",[]')
        datos_ciudad = check_type(datos_ciudad)
        if ciudad not in tabla:
            tabla[ciudad] = datos_ciudad
        else:
            for k in datos_ciudad:
                if datos_ciudad[k] not in FALLOS:
                    if k not in tabla[ciudad]:
                        tabla[ciudad][k] = str(datos_ciudad[k])
                    tabla[ciudad][k] += "\n---\n" + str(datos_ciudad[k])
    return tabla

# Función para obtener información extra de Turismo y fusionarla con Wikipedia
def recolectar_datos_reforzados():
    tabla = cargar_json_existente()
    tabla = recolectar_datos_wikipedia(tabla)  # Primero obtenemos los datos de Wikipedia

    for ciudad in CIUDADES:
        print(f"Reforzando datos para {ciudad} con información externa...")
        texto_turismo = obtener_texto_turismo(ciudad)
        prompt = generar_prompt_otras_fuentes(ciudad, texto_turismo, DATOS)
        respuesta = ask_deepseek(prompt)
        limpia = limpiar_respuesta(respuesta)
        datos_ciudad = {}
        try:
            datos_ciudad = json.loads(limpia)
        except json.JSONDecodeError:
            try:
                datos_ciudad = ast.literal_eval(limpia)
            except Exception:
                json_aprox = re.findall(r'"([^"]+)"\s*:\s*(.*?)(,|\n|$)', limpia)
                for clave, valor, _ in json_aprox:
                    match = get_close_matches(clave.strip(), DATOS, n=1, cutoff=0.4)
                    if match:
                        datos_ciudad[match[0]] = valor.strip().strip('",[]')
        datos_ciudad = check_type(datos_ciudad)
        if ciudad not in tabla:
            tabla[ciudad] = datos_ciudad
        else:
            for k in datos_ciudad:
                if datos_ciudad[k] not in FALLOS:
                    if k not in tabla[ciudad]:
                        tabla[ciudad][k] = str(datos_ciudad[k])
                    tabla[ciudad][k] += "\n---\n" + str(datos_ciudad[k])
    return tabla

# Función que guarda los resultados en un archivo JSON y TXT
def guardar_resultados(tabla):
    with open(TXT_OUTPUT_PATH, "w", encoding="utf-8") as f_txt:
        for ciudad, datos in tabla.items():
            f_txt.write(f"{ciudad}:\n")
            for k, v in datos.items():
                f_txt.write(f"  {k}: {v}\n")
            f_txt.write("\n")

    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f_json:
        json.dump(tabla, f_json, ensure_ascii=False, indent=4)

# === EJECUCIÓN ===
if __name__ == "__main__":
    tabla_reforzada = recolectar_datos_reforzados()
    guardar_resultados(tabla_reforzada)
    print("Proceso completado.")