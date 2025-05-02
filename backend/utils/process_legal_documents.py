#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar documentos legales (PDF y RTF) y extraer metadatos
para generar archivos JSON estructurados.

Este script analiza documentos legales en ./Docs/BaseDeDatos/ y genera
archivos JSON en ./Docs/BaseDeDatos/json_output/
"""

import os
import re
import json
import logging
import shutil
import unicodedata
import string
from datetime import datetime
from pathlib import Path
from collections import Counter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Verificar e instalar dependencias
try:
    import PyPDF2
except ImportError:
    logger.info("Instalando PyPDF2...")
    os.system("pip install PyPDF2")
    import PyPDF2

try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    logger.info("Instalando striprtf...")
    os.system("pip install striprtf")
    from striprtf.striprtf import rtf_to_text

# Constantes
BASE_DIR = "./Docs/BaseDeDatos"
OUTPUT_DIR = os.path.join(BASE_DIR, "json_output")
CATEGORIAS_LEGALES = [
    "ley", "decreto", "sentencia", "circular", "resolución", "concepto", 
    "guía", "cartilla", "jurisprudencia", "doctrina"
]

# Patrones para identificar documentos legales
PATRONES_LEY = re.compile(r"[lL]ey\s+(\d+)\s+de\s+(\d{4})")
PATRONES_DECRETO = re.compile(r"[dD]ecreto\s+(\d+)\s+de\s+(\d{4})")
PATRONES_SENTENCIA = re.compile(r"[sS]entencia\s+([A-Z]-\d+-\d+|[A-Z]{1,2}\d+(-|\s+)\d+)")
PATRONES_RESOLUCION = re.compile(r"[rR]esolución\s+(\d+)\s+de\s+(\d{4})")
PATRONES_FECHA = re.compile(r"(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})", re.IGNORECASE)

# Palabras clave relacionadas con derecho laboral
PALABRAS_CLAVE_LABORAL = [
    "contrato", "trabajo", "laboral", "empleador", "empleado", "trabajador", 
    "despido", "indemnización", "salario", "prestaciones", "seguridad social",
    "pensión", "cesantía", "vacaciones", "primas", "licencia", "incapacidad",
    "maternidad", "paternidad", "jornada", "horas extras", "descanso", "dominical",
    "sindicato", "huelga", "acoso laboral", "terminación", "liquidación", "carga",
    "subordinación", "remuneración", "modalidad", "suspensión", "horario",
    "discriminación", "estabilidad", "fuero", "convención", "colectivo"
]

# Palabras vacías en español
PALABRAS_VACIAS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
    "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella",
    "ellas", "ellos", "en", "entre", "era", "erais", "eran", "eras", "eres", "es",
    "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estabais", "estaban",
    "estabas", "estad", "estada", "estadas", "estado", "estados", "estamos", "estando",
    "estar", "estaremos", "estará", "estarán", "estarás", "estaré", "estaréis",
    "estaría", "estaríais", "estaríamos", "estarían", "estarías", "estas", "este",
    "estemos", "esto", "estos", "estoy", "estuve", "estuviera", "estuvierais",
    "estuvieran", "estuvieras", "estuvieron", "estuviese", "estuvieseis", "estuviesen",
    "estuvieses", "estuvimos", "estuviste", "estuvisteis", "estuviéramos",
    "estuviésemos", "estuvo", "está", "estábamos", "estáis", "están", "estás", "esté",
    "estéis", "estén", "estés", "fue", "fuera", "fuerais", "fueran", "fueras",
    "fueron", "fuese", "fueseis", "fuesen", "fueses", "fui", "fuimos", "fuiste",
    "fuisteis", "fuéramos", "fuésemos", "ha", "habida", "habidas", "habido", "habidos",
    "habiendo", "habremos", "habrá", "habrán", "habrás", "habré", "habréis", "habría",
    "habríais", "habríamos", "habrían", "habrías", "habéis", "había", "habíais",
    "habíamos", "habían", "habías", "han", "has", "hasta", "hay", "haya", "hayamos",
    "hayan", "hayas", "hayáis", "he", "hemos", "hube", "hubiera", "hubierais",
    "hubieran", "hubieras", "hubieron", "hubiese", "hubieseis", "hubiesen", "hubieses",
    "hubimos", "hubiste", "hubisteis", "hubiéramos", "hubiésemos", "hubo", "la", "las",
    "le", "les", "lo", "los", "me", "mi", "mis", "mucho", "muchos", "muy", "más",
    "mí", "mía", "mías", "mío", "míos", "nada", "ni", "no", "nos", "nosotras",
    "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "o", "os", "otra",
    "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "que",
    "quien", "quienes", "qué", "se", "sea", "seamos", "sean", "seas", "seremos",
    "será", "serán", "serás", "seré", "seréis", "sería", "seríais", "seríamos",
    "serían", "serías", "seáis", "sido", "siendo", "sin", "sobre", "sois", "somos",
    "son", "soy", "su", "sus", "suya", "suyas", "suyo", "suyos", "sí", "también",
    "tanto", "te", "tendremos", "tendrá", "tendrán", "tendrás", "tendré", "tendréis",
    "tendría", "tendríais", "tendríamos", "tendrían", "tendrías", "tened", "tenemos",
    "tenga", "tengamos", "tengan", "tengas", "tengo", "tengáis", "tenida", "tenidas",
    "tenido", "tenidos", "teniendo", "tenéis", "tenía", "teníais", "teníamos", "tenían",
    "tenías", "ti", "tiene", "tienen", "tienes", "todo", "todos", "tu", "tus", "tuve",
    "tuviera", "tuvierais", "tuvieran", "tuvieras", "tuvieron", "tuviese", "tuvieseis",
    "tuviesen", "tuvieses", "tuvimos", "tuviste", "tuvisteis", "tuviéramos",
    "tuviésemos", "tuvo", "tuya", "tuyas", "tuyo", "tuyos", "tú", "un", "una", "uno",
    "unos", "vosotras", "vosotros", "vuestra", "vuestras", "vuestro", "vuestros", "y",
    "ya", "yo", "él", "éramos"
}

def normalize_text(text):
    """Normaliza un texto para eliminar caracteres extraños y problemas de codificación"""
    if text is None:
        return ""
    
    # Normalizar espacios y saltos de línea
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Normalizar Unicode
    text = unicodedata.normalize('NFKD', text)
    
    return text

def extract_text_from_pdf(file_path):
    """Extrae el texto completo de un archivo PDF"""
    logger.info(f"Extrayendo texto de PDF: {file_path}")
    
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extraer texto de cada página
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error al procesar el PDF {file_path}: {str(e)}")
        return ""
    
    return normalize_text(text)

def extract_text_from_rtf(file_path):
    """Extrae el texto completo de un archivo RTF"""
    logger.info(f"Extrayendo texto de RTF: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            rtf_text = file.read()
            text = rtf_to_text(rtf_text)
    except Exception as e:
        logger.error(f"Error al procesar el RTF {file_path}: {str(e)}")
        return ""
    
    return normalize_text(text)

def extract_text_from_docx(file_path):
    """Extrae el texto completo de un archivo DOCX"""
    logger.info(f"Extrayendo texto de DOCX: {file_path}")
    
    try:
        import docx
    except ImportError:
        logger.info("Instalando python-docx...")
        os.system("pip install python-docx")
        import docx
    
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logger.error(f"Error al procesar el DOCX {file_path}: {str(e)}")
        return ""
    
    return normalize_text(text)

def extract_keywords(text, n=5):
    """Extrae palabras clave del texto utilizando un enfoque de frecuencia de palabras"""
    # Normalizar texto
    text = text.lower()
    
    # Eliminar puntuación y dividir el texto en palabras
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    words = text.split()
    
    # Filtrar palabras vacías y palabras cortas
    filtered_words = [word for word in words if word not in PALABRAS_VACIAS and len(word) > 3]
    
    # Contar frecuencia de palabras
    word_counts = Counter(filtered_words)
    
    # Obtener las n palabras más frecuentes
    most_common = [word for word, _ in word_counts.most_common(n)]
    
    # Buscar palabras clave específicas de derecho laboral
    labor_keywords = []
    for keyword in PALABRAS_CLAVE_LABORAL:
        if keyword.lower() in text and keyword not in most_common and keyword not in labor_keywords:
            labor_keywords.append(keyword)
            if len(labor_keywords) >= 5:  # Limitar a 5 palabras clave adicionales
                break
    
    # Combinar y asegurar al menos 3 palabras clave
    all_keywords = most_common + labor_keywords
    if len(all_keywords) < 3:
        # Si no tenemos suficientes palabras clave, añadir algunas genéricas
        generic_keywords = ["derecho", "laboral", "colombia"]
        for kw in generic_keywords:
            if kw not in all_keywords:
                all_keywords.append(kw)
            if len(all_keywords) >= 3:
                break
    
    return all_keywords[:10]  # Limitar a 10 palabras clave

def extract_date(text):
    """Extrae la fecha del documento en formato YYYY-MM-DD"""
    # Buscar patrones comunes de fecha
    months_map = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    # Buscar patrones como "12 de enero de 2023"
    match = PATRONES_FECHA.search(text)
    if match:
        day, month, year = match.groups()
        day = day.zfill(2)
        month = months_map.get(month.lower(), '01')
        return f"{year}-{month}-{day}"
    
    # Buscar patrones como "2023-01-12"
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        return match.group(0)
    
    # Buscar patrones en nombres de archivo como "ley-2121-del-3-de-agosto-de-2021.pdf"
    match = re.search(r"(\d{4})\.(?:pdf|rtf|docx)$", text)
    if match:
        return f"{match.group(1)}-01-01"  # Año con mes y día por defecto
    
    # Buscar cualquier año de 4 dígitos en el texto
    match = re.search(r"(\d{4})", text)
    if match:
        return f"{match.group(1)}-01-01 (estimado)"
    
    # Si no encontramos fecha, devolvemos una estimación
    current_year = datetime.now().year
    return f"{current_year}-01-01 (estimado)"

def extract_title(text, filename):
    """Extrae el título del documento"""
    # Intentar extraer del texto
    lines = text.split('\n')
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        if len(line) > 15 and len(line) < 200:
            return line
    
    # Si no encontramos, usar el nombre del archivo
    base_name = os.path.basename(filename)
    name_without_ext = os.path.splitext(base_name)[0]
    name_clean = re.sub(r'[_-]', ' ', name_without_ext)
    
    return name_clean

def extract_category(text, filename):
    """Determina la categoría del documento legal"""
    filename_lower = filename.lower()
    text_lower = text.lower()[:1000]  # Primeros 1000 caracteres
    
    # Comprobar nombre de archivo y texto para categorías comunes
    if re.search(r'ley|legislación', filename_lower) or PATRONES_LEY.search(text_lower):
        return "ley"
    elif re.search(r'decreto', filename_lower) or PATRONES_DECRETO.search(text_lower):
        return "decreto"
    elif re.search(r'sentencia|[ct]-\d+', filename_lower) or PATRONES_SENTENCIA.search(text_lower):
        return "sentencia"
    elif re.search(r'resolución|resolución|res', filename_lower) or PATRONES_RESOLUCION.search(text_lower):
        return "resolución"
    elif re.search(r'circular', filename_lower) or re.search(r'circular', text_lower):
        return "circular"
    elif re.search(r'concepto', filename_lower) or re.search(r'concepto', text_lower):
        return "concepto"
    elif re.search(r'guía|guia', filename_lower):
        return "guía"
    elif re.search(r'cartilla', filename_lower):
        return "cartilla"
    
    # Si no encontramos categoría específica
    for cat in CATEGORIAS_LEGALES:
        if re.search(cat, text_lower):
            return cat
    
    return "documento legal (no especificado)"

def extract_subcategory(text, category):
    """Extrae la subcategoría del documento"""
    text_lower = text.lower()
    
    # Subcategorías para sentencias
    if category == "sentencia":
        if re.search(r'constitucional|corte constitucional', text_lower):
            return "constitucional"
        elif re.search(r'suprema|corte suprema|casación', text_lower):
            return "casación laboral"
        elif re.search(r'tutela|acción de tutela', text_lower):
            return "tutela"
        elif re.search(r'consejo de estado', text_lower):
            return "consejo de estado"
    
    # Subcategorías para leyes
    elif category == "ley":
        if re.search(r'estatutaria', text_lower):
            return "estatutaria"
        elif re.search(r'orgánica|organica', text_lower):
            return "orgánica"
        else:
            return "ordinaria"
    
    # Subcategorías laborales
    if re.search(r'contrato|laboral|trabajo', text_lower):
        return "derecho laboral"
    elif re.search(r'seguridad social|pensión|salud', text_lower):
        return "seguridad social"
    elif re.search(r'sindical|sindicato|colectiv', text_lower):
        return "derecho colectivo"
    
    return ""

def extract_reference_number(text, filename, category):
    """Extrae el número de referencia del documento"""
    filename_lower = filename.lower()
    text_lower = text.lower()[:2000]  # Primeros 2000 caracteres
    
    # Patrones según categoría
    if category == "ley":
        match = PATRONES_LEY.search(text_lower)
        if match:
            return f"Ley {match.group(1)} de {match.group(2)}"
        
        # Buscar en nombre de archivo (ej: ley-2121-del-3-de-agosto-de-2021.pdf)
        match = re.search(r'ley[_-]?(\d+)[_-](?:de|del)[_-]?.+(\d{4})', filename_lower)
        if match:
            return f"Ley {match.group(1)} de {match.group(2)}"
    
    elif category == "decreto":
        match = PATRONES_DECRETO.search(text_lower)
        if match:
            return f"Decreto {match.group(1)} de {match.group(2)}"
    
    elif category == "sentencia":
        match = PATRONES_SENTENCIA.search(text_lower) or re.search(r'([ct]-\d+-\d+)', filename_lower, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar en nombre de archivo (ej: T-329-22.rtf)
        match = re.search(r'([a-z]-\d+-\d+|[a-z]{1,2}\d+(-|\s+)\d+)', filename_lower)
        if match:
            return match.group(1).upper()
    
    elif category == "resolución":
        match = PATRONES_RESOLUCION.search(text_lower)
        if match:
            return f"Resolución {match.group(1)} de {match.group(2)}"
        
        # Buscar en nombre de archivo
        match = re.search(r'res[_-]?(\d+)[_-](?:de|del)?[_-]?(\d{4})?', filename_lower)
        if match:
            year = match.group(2) if match.group(2) else datetime.now().year
            return f"Resolución {match.group(1)} de {year}"
    
    # Si no encontramos un patrón específico, extraer cualquier número de referencia
    match = re.search(r'(?:No\.|Número|N°|#)\s*(\d+[\w-]*\d*)', text_lower)
    if match:
        return match.group(1)
    
    # Si todo falla, extraer números del nombre del archivo
    match = re.search(r'(\d+)', filename_lower)
    if match:
        return f"Ref. {match.group(1)}"
    
    return "Sin número de referencia"

def extract_source(text, category):
    """Extrae la fuente del documento"""
    text_lower = text.lower()
    
    # Fuentes comunes según categoría
    if category == "ley":
        return "Congreso de la República de Colombia"
    
    elif category == "decreto":
        if re.search(r'president', text_lower):
            return "Presidencia de la República de Colombia"
        else:
            return "Gobierno Nacional de Colombia"
    
    elif category == "sentencia":
        if re.search(r'corte constitucional', text_lower):
            return "Corte Constitucional de Colombia"
        elif re.search(r'corte suprema', text_lower):
            return "Corte Suprema de Justicia de Colombia"
        elif re.search(r'consejo de estado', text_lower):
            return "Consejo de Estado de Colombia"
        else:
            return "Rama Judicial de Colombia"
    
    elif category == "resolución" or category == "circular" or category == "concepto":
        if re.search(r'minist\w+ (?:del? )?trabajo', text_lower):
            return "Ministerio del Trabajo de Colombia"
        elif re.search(r'superintendencia', text_lower):
            if re.search(r'sociedades', text_lower):
                return "Superintendencia de Sociedades de Colombia"
            else:
                return "Superintendencia de Colombia"
    
    # Intentar encontrar cualquier institución
    instituciones = [
        ("Ministerio del Trabajo", r'minist\w+ (?:del? )?trabajo'),
        ("Corte Constitucional", r'corte constitucional'),
        ("Corte Suprema de Justicia", r'corte suprema'),
        ("Consejo de Estado", r'consejo de estado'),
        ("Superintendencia de Sociedades", r'superintendencia de sociedades'),
        ("Fiscalía General de la Nación", r'fiscalía'),
        ("Procuraduría General de la Nación", r'procuraduría'),
        ("Congreso de la República", r'congreso'),
        ("Presidencia de la República", r'presiden\w+'),
        ("DIAN", r'\bDIAN\b')
    ]
    
    for nombre, patron in instituciones:
        if re.search(patron, text_lower):
            return nombre
    
    return "Fuente no identificada"

def generate_summary(text, max_lines=6):
    """Genera un resumen del documento"""
    # Usar las primeras líneas relevantes como resumen
    lines = text.split('\n')
    summary_lines = []
    skip_patterns = [r'^página \d+$', r'^\s*$', r'^[\d\.]+$']
    
    for line in lines:
        line = line.strip()
        # Saltar líneas que son irrelevantes
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
        
        # Saltar líneas demasiado cortas
        if len(line) < 20:
            continue
        
        summary_lines.append(line)
        if len(summary_lines) >= max_lines:
            break
    
    # Si no hemos encontrado suficientes líneas, buscar más en el texto
    if len(summary_lines) < 2:
        # Buscar frases completas
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:
                summary_lines.append(sentence)
                if len(summary_lines) >= max_lines:
                    break
    
    summary = ' '.join(summary_lines)
    
    # Truncar si es demasiado largo
    if len(summary) > 1000:
        summary = summary[:997] + "..."
    
    return summary

def is_labor_law_document(text):
    """Determina si un documento es relevante para derecho laboral"""
    text_lower = text.lower()
    
    # Palabras clave de derecho laboral
    labor_patterns = [
        r'contrato(?:\s+de)?\s+trabajo', r'derecho\s+laboral', r'código\s+(?:sustantivo\s+(?:del|de))?\s+trabajo',
        r'empleador', r'trabajador', r'salario', r'jornada\s+(?:de)?\s+trabajo', r'horas\s+extras',
        r'prestaciones\s+sociales', r'indemnización', r'despido', r'cesantías', r'pensión',
        r'seguridad\s+social', r'vacaciones', r'primas', r'licencia\s+(?:de)?\s+maternidad', 
        r'licencia\s+(?:de)?\s+paternidad', r'incapacidad\s+laboral', r'subordinación',
        r'terminación\s+(?:del|de)?\s+contrato', r'sindicato', r'negociación\s+colectiva', r'huelga',
        r'acoso\s+laboral', r'ministerio\s+(?:del)?\s+trabajo', r'fuero\s+(?:de)?\s+estabilidad', 
        r'estabilidad\s+laboral\s+reforzada', r'liquidación', r'remuneración', r'cotización'
    ]
    
    # Contamos cuántas palabras clave aparecen
    matches = 0
    for pattern in labor_patterns:
        if re.search(pattern, text_lower):
            matches += 1
    
    # Si hay al menos 3 coincidencias o hay términos específicos, es relevante
    if matches >= 3 or any(re.search(r'código\s+(?:sustantivo\s+)(?:del|de)?\s+trabajo|derecho\s+laboral', text_lower)):
        return True, ""
    
    # Si el texto es corto y no encontramos coincidencias
    if len(text) < 1000 and matches == 0:
        return False, "Documento demasiado breve sin términos de derecho laboral"
    
    if matches < 3:
        return False, f"Documento contiene solo {matches} términos relacionados con derecho laboral (mínimo 3)"
    
    return False, "No se identificaron suficientes elementos de derecho laboral colombiano"

def process_document(file_path):
    """Procesa un documento y extrae sus metadatos"""
    logger.info(f"Procesando: {file_path}")
    
    # Obtener extensión
    file_extension = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    
    # Extraer texto según formato
    if file_extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension == '.rtf':
        text = extract_text_from_rtf(file_path)
    elif file_extension == '.docx':
        text = extract_text_from_docx(file_path)
    else:
        logger.warning(f"Formato no soportado: {file_extension}")
        return None
    
    # Verificar si hay suficiente texto
    if len(text) < 100:
        logger.warning(f"Texto insuficiente en {file_path}")
        return {
            "titulo": os.path.basename(file_path),
            "categoria": "desconocido",
            "subcategoria": "",
            "fecha": datetime.now().strftime("%Y-%m-%d") + " (estimado)",
            "numero": "",
            "fuente": "desconocido",
            "palabras_clave": [],
            "resumen": "No se pudo extraer texto del documento",
            "texto_completo": text,
            "pertinente": False,
            "razon_exclusion": "No se pudo extraer suficiente texto del documento"
        }
    
    # Verificar si es relevante para derecho laboral
    is_relevant, reason = is_labor_law_document(text)
    
    # Extraer metadatos
    category = extract_category(text, filename)
    
    metadata = {
        "titulo": extract_title(text, filename),
        "categoria": category,
        "subcategoria": extract_subcategory(text, category),
        "fecha": extract_date(text),
        "numero": extract_reference_number(text, filename, category),
        "fuente": extract_source(text, category),
        "palabras_clave": extract_keywords(text),
        "resumen": generate_summary(text),
        "texto_completo": text,
        "pertinente": is_relevant,
    }
    
    if not is_relevant:
        metadata["razon_exclusion"] = reason
    
    return metadata

def validate_json_format(json_data):
    """Valida que el formato JSON sea correcto"""
    try:
        # Verificar campos obligatorios
        required_fields = ["titulo", "categoria", "fecha", "numero", "fuente", 
                          "palabras_clave", "resumen", "texto_completo", "pertinente"]
        
        for field in required_fields:
            if field not in json_data:
                return False, f"Campo obligatorio '{field}' faltante"
        
        # Verificar tipos de datos
        if not isinstance(json_data["titulo"], str):
            return False, "Campo 'titulo' debe ser texto"
        
        if not isinstance(json_data["categoria"], str):
            return False, "Campo 'categoria' debe ser texto"
        
        if not isinstance(json_data["palabras_clave"], list):
            return False, "Campo 'palabras_clave' debe ser una lista"
        
        if not isinstance(json_data["pertinente"], bool):
            return False, "Campo 'pertinente' debe ser booleano"
        
        # Verificar campo 'razon_exclusion' si pertinente es False
        if not json_data["pertinente"] and "razon_exclusion" not in json_data:
            return False, "Campo 'razon_exclusion' obligatorio cuando 'pertinente' es False"
        
        return True, "JSON válido"
    
    except Exception as e:
        return False, f"Error de validación: {str(e)}"

def main():
    """Función principal para procesar todos los documentos"""
    # Crear directorio de salida si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Directorio creado: {OUTPUT_DIR}")
    
    # Listar archivos en el directorio
    total_files = 0
    success_count = 0
    error_count = 0
    
    # Documentos a procesar (PDF y RTF)
    for file in os.listdir(BASE_DIR):
        file_path = os.path.join(BASE_DIR, file)
        
        # Saltar directorios y archivos que no son documentos
        if os.path.isdir(file_path) or not os.path.isfile(file_path):
            continue
        
        # Verificar extensión
        file_extension = os.path.splitext(file)[1].lower()
        if file_extension not in ['.pdf', '.rtf', '.docx']:
            continue
        
        total_files += 1
        
        try:
            # Procesar documento
            metadata = process_document(file_path)
            
            if metadata:
                # Generar nombre de archivo para el JSON
                json_filename = os.path.splitext(file)[0] + '.json'
                json_path = os.path.join(OUTPUT_DIR, json_filename)
                
                # Guardar en formato JSON
                with open(json_path, 'w', encoding='utf-8') as json_file:
                    json.dump(metadata, json_file, ensure_ascii=False, indent=2)
                
                # Validar formato JSON
                is_valid, validation_msg = validate_json_format(metadata)
                
                if is_valid:
                    logger.info(f"✓ JSON generado y validado: {json_filename}")
                    success_count += 1
                else:
                    logger.warning(f"⚠ JSON con formato incorrecto: {json_filename} - {validation_msg}")
                    error_count += 1
            else:
                logger.error(f"✗ No se pudo procesar: {file}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"✗ Error procesando {file}: {str(e)}")
            error_count += 1
    
    # Resumen final
    logger.info(f"\n{'='*50}")
    logger.info(f"RESUMEN DE PROCESAMIENTO")
    logger.info(f"{'='*50}")
    logger.info(f"Total de archivos encontrados: {total_files}")
    logger.info(f"Archivos procesados exitosamente: {success_count}")
    logger.info(f"Errores de procesamiento: {error_count}")
    logger.info(f"Archivos JSON generados en: {OUTPUT_DIR}")
    logger.info(f"{'='*50}")

if __name__ == "__main__":
    logger.info("Iniciando procesamiento de documentos legales")
    main()
    logger.info("Procesamiento completado") 