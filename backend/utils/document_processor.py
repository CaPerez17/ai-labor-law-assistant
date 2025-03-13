"""
Procesador de Documentos Legales
-----------------------------
Este módulo implementa funciones para extraer texto de documentos legales,
preprocesarlos y generar metadatos estructurados para cargarlos en la base de datos.
"""

import os
import re
import sys
import json
import fitz  # PyMuPDF
import nltk
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from dateutil import parser as date_parser

# Asegurarnos de que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Descargar recursos NLTK necesarios (ejecutar solo una vez)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Patrones para identificar tipos de documentos legales
DOCUMENT_PATTERNS = {
    "ley": r"ley\s+(?:no\.?|número)?\s*\d+|artículo\s+\d+|código\s+(?:sustantivo|penal|civil)",
    "decreto": r"decreto\s+(?:no\.?|número)?\s*\d+",
    "sentencia": r"sentencia\s+(?:no\.?|número)?\s*[a-z0-9\-]+",
    "resolución": r"resolución\s+(?:no\.?|número)?\s*\d+",
    "circular": r"circular\s+(?:no\.?|número)?\s*\d+",
    "concepto": r"concepto\s+(?:no\.?|número)?\s*\d+"
}

# Patrones para extraer referencias 
REFERENCE_PATTERNS = {
    "ley": r"ley\s+(?:no\.?|número)?\s*(\d+)\s+(?:de\s+(\d{4}))?",
    "decreto": r"decreto\s+(?:no\.?|número)?\s*(\d+)\s+(?:de\s+(\d{4}))?",
    "sentencia": r"sentencia\s+(?:no\.?|número)?\s*([a-z0-9\-]+)\s+(?:de\s+(\d{4}))?",
    "artículo": r"artículo\s+(\d+)",
    "cst": r"c(?:ódigo)?\s*s(?:ustantivo)?\s*(?:del)?\s*t(?:rabajo)?"
}

# Categorías laborales y subcategorías
LABOR_CATEGORIES = {
    "licencias": ["maternidad", "paternidad", "incapacidad", "calamidad"],
    "salarios": ["mínimo", "integral", "auxilio", "prestaciones", "cesantías"],
    "contratos": ["término fijo", "indefinido", "obra labor", "prestación servicios"],
    "terminación": ["indemnización", "despido", "justa causa", "sin justa causa"],
    "protección": ["estabilidad", "reforzada", "fuero", "acoso laboral"]
}

# Palabras clave adicionales para categorías
CATEGORY_KEYWORDS = {
    "licencias": ["licencia", "permiso", "autorización", "ausencia"],
    "salarios": ["remuneración", "pago", "salario", "sueldo", "prima", "bonificación"],
    "contratos": ["contrato", "vinculación", "relación laboral", "empleador", "trabajador"],
    "terminación": ["terminación", "despido", "renuncia", "finalización", "liquidación"],
    "protección": ["protección", "fuero", "estabilidad", "discriminación", "acoso"]
}

class DocumentProcessor:
    """Clase para procesar documentos legales y extraer su contenido y metadatos"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('spanish'))
        # Palabras adicionales específicas del dominio legal que no son relevantes para el análisis
        self.legal_stop_words = {
            'artículo', 'ley', 'decreto', 'sentencia', 'resolución', 'código', 'artículos', 
            'leyes', 'decretos', 'sentencias', 'resoluciones', 'códigos'
        }
        self.stop_words.update(self.legal_stop_words)
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error(f"Error al procesar PDF {file_path}: {e}")
            return ""
            
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extrae texto de un archivo TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Intentar con otra codificación
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error al leer TXT {file_path}: {e}")
                return ""
        except Exception as e:
            logger.error(f"Error al procesar TXT {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extrae texto de un archivo según su extensión"""
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            logger.warning(f"Tipo de archivo no soportado: {file_ext}")
            return ""
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesa el texto: normalización y limpieza"""
        if not text:
            return ""
            
        # Convertir a minúsculas
        text = text.lower()
        
        # Normalizar espacios y saltos de línea
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar caracteres especiales pero conservar acentos y ñ
        text = re.sub(r'[^\w\sáéíóúüñ.,;:\-()"]', ' ', text)
        
        return text.strip()
    
    def tokenize_text(self, text: str) -> List[str]:
        """Tokeniza el texto eliminando stopwords"""
        if not text:
            return []
            
        tokens = word_tokenize(text, language='spanish')
        # Eliminar stopwords y tokens cortos
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return tokens
        
    def detect_document_type(self, text: str) -> str:
        """Detecta el tipo de documento basado en patrones"""
        text = text.lower()
        
        for doc_type, pattern in DOCUMENT_PATTERNS.items():
            if re.search(pattern, text):
                return doc_type
                
        return "otro"  # Tipo por defecto
    
    def extract_reference_number(self, text: str, doc_type: str) -> str:
        """Extrae el número de referencia del documento"""
        text = text.lower()
        
        # Buscar patrones específicos según el tipo de documento
        if doc_type == "ley":
            match = re.search(REFERENCE_PATTERNS["ley"], text)
            if match:
                num, year = match.groups()
                return f"Ley {num}" + (f" de {year}" if year else "")
                
            # Buscar CST
            match = re.search(REFERENCE_PATTERNS["cst"], text)
            if match:
                # Buscar número de artículo
                art_match = re.search(REFERENCE_PATTERNS["artículo"], text)
                if art_match:
                    return f"CST-Art {art_match.group(1)}"
                return "CST"
                
        elif doc_type == "decreto":
            match = re.search(REFERENCE_PATTERNS["decreto"], text)
            if match:
                num, year = match.groups()
                return f"Decreto {num}" + (f" de {year}" if year else "")
                
        elif doc_type == "sentencia":
            match = re.search(REFERENCE_PATTERNS["sentencia"], text)
            if match:
                ref, year = match.groups()
                return f"Sentencia {ref}" + (f" de {year}" if year else "")
                
        # Extraer primeros 30 caracteres como referencia para otros casos
        return text[:30].strip() + "..."
    
    def extract_date(self, text: str) -> Optional[datetime]:
        """Intenta extraer una fecha del texto"""
        # Patrones comunes de fechas en español
        date_patterns = [
            r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    try:
                        # Convertir el match a string para date_parser
                        date_str = ' '.join(match)
                        return date_parser.parse(date_str, fuzzy=True)
                    except:
                        continue
        
        # Si no se encontró una fecha específica, intentar buscar solo un año
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
        if year_match:
            try:
                return datetime(int(year_match.group(1)), 1, 1)  # Usar 1 de enero del año encontrado
            except:
                pass
                
        return None
    
    def extract_categories(self, tokens: List[str]) -> Tuple[str, str]:
        """Identifica la categoría y subcategoría del documento"""
        # Contar apariciones de palabras clave para cada categoría
        category_scores = {cat: 0 for cat in LABOR_CATEGORIES.keys()}
        
        # Contar coincidencias de tokens con palabras clave por categoría
        for token in tokens:
            for category, keywords in CATEGORY_KEYWORDS.items():
                for keyword in keywords:
                    if token in keyword or keyword in token:
                        category_scores[category] += 1
        
        # Identificar la categoría con mayor puntuación
        if not category_scores or max(category_scores.values()) == 0:
            return "General", "Otro"
            
        main_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Determinar subcategoría
        subcategory_scores = {subcat: 0 for subcat in LABOR_CATEGORIES[main_category]}
        for token in tokens:
            for subcat in LABOR_CATEGORIES[main_category]:
                if token in subcat or subcat in token:
                    subcategory_scores[subcat] += 1
        
        if not subcategory_scores or max(subcategory_scores.values()) == 0:
            return main_category.capitalize(), "Otro"
            
        subcategory = max(subcategory_scores.items(), key=lambda x: x[1])[0]
        return main_category.capitalize(), subcategory.capitalize()
    
    def extract_keywords(self, tokens: List[str], max_keywords: int = 10) -> str:
        """Extrae palabras clave relevantes del texto"""
        # Contar frecuencia de tokens
        freq = {}
        for token in tokens:
            if token in freq:
                freq[token] += 1
            else:
                freq[token] = 1
                
        # Ordenar por frecuencia y tomar las más comunes
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [token for token, _ in sorted_tokens[:max_keywords]]
        
        return ", ".join(top_keywords)
    
    def extract_title(self, text: str) -> str:
        """Intenta extraer un título del documento"""
        # Dividir en líneas y tomar las primeras no vacías
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return "Documento sin título"
            
        # Generalmente el título está al principio y es relativamente corto
        potential_titles = [line for line in lines[:5] if 10 < len(line) < 100]
        
        if potential_titles:
            return potential_titles[0]
        else:
            # Si no hay líneas que parezcan títulos, tomar la primera línea
            return lines[0][:100]
    
    def extract_source(self, text: str) -> str:
        """Intenta identificar la fuente o entidad emisora"""
        # Patrones comunes de fuentes o entidades emisoras
        source_patterns = [
            r'ministerio\s+de\s+([a-záéíóúüñ\s]+)',
            r'(corte\s+(?:constitucional|suprema))',
            r'(congreso\s+(?:de\s+la\s+república|de\s+colombia))',
            r'presidencia\s+de\s+(?:la\s+república|colombia)',
            r'(consejo\s+de\s+estado)'
        ]
        
        for pattern in source_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(0).title()
                
        return "Desconocido"
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Procesa un documento y extrae toda la información relevante"""
        # Extraer texto según el tipo de archivo
        raw_text = self.extract_text(file_path)
        if not raw_text:
            return None
            
        # Preprocesar el texto
        processed_text = self.preprocess_text(raw_text)
        
        # Tokenizar para análisis
        tokens = self.tokenize_text(processed_text)
        
        # Detectar tipo de documento
        doc_type = self.detect_document_type(processed_text)
        
        # Extraer título
        title = self.extract_title(raw_text)
        
        # Crear diccionario con la información extraída
        document_info = {
            "title": title,
            "document_type": doc_type,
            "reference_number": self.extract_reference_number(processed_text, doc_type),
            "issue_date": self.extract_date(processed_text),
            "source": self.extract_source(processed_text),
            "content": raw_text,  # Guardamos el texto original completo
            "keywords": self.extract_keywords(tokens),
        }
        
        # Extraer categoría y subcategoría
        category, subcategory = self.extract_categories(tokens)
        document_info["category"] = category
        document_info["subcategory"] = subcategory
        
        # Retornar resultado
        return document_info
        
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Procesa todos los documentos en un directorio"""
        results = []
        
        # Listar todos los archivos en el directorio
        for root, _, files in os.walk(directory_path):
            for file in files:
                # Comprobar si es un tipo de archivo soportado
                if file.lower().endswith(('.pdf', '.txt')):
                    file_path = os.path.join(root, file)
                    logger.info(f"Procesando archivo: {file_path}")
                    
                    # Procesar documento
                    doc_info = self.process_document(file_path)
                    if doc_info:
                        results.append(doc_info)
                        logger.info(f"Documento procesado: {doc_info['title']}")
                    else:
                        logger.warning(f"Error al procesar documento: {file_path}")
        
        return results 