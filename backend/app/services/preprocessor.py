import PyPDF2
import docx
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def procesar_documento(path: str) -> str:
    """
    Procesa un documento y extrae su texto.
    Soporta PDF y DOCX.
    """
    try:
        if path.lower().endswith('.pdf'):
            return _procesar_pdf(path)
        elif path.lower().endswith('.docx'):
            return _procesar_docx(path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {path}")
    except Exception as e:
        logger.error(f"Error procesando documento {path}: {str(e)}")
        raise

def _procesar_pdf(path: str) -> str:
    """Extrae texto de un archivo PDF."""
    texto = []
    try:
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto.append(page.extract_text())
        return _limpiar_texto(' '.join(texto))
    except Exception as e:
        logger.error(f"Error procesando PDF {path}: {str(e)}")
        raise

def _procesar_docx(path: str) -> str:
    """Extrae texto de un archivo DOCX."""
    try:
        doc = docx.Document(path)
        texto = []
        for para in doc.paragraphs:
            texto.append(para.text)
        return _limpiar_texto('\n'.join(texto))
    except Exception as e:
        logger.error(f"Error procesando DOCX {path}: {str(e)}")
        raise

def _limpiar_texto(texto: str) -> str:
    """Limpia el texto extraído."""
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    # Eliminar caracteres especiales
    texto = re.sub(r'[^\w\s.,;:¿?¡!()]', '', texto)
    # Normalizar espacios
    texto = texto.strip()
    return texto 