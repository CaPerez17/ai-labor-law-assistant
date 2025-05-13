"""
Esquemas para el análisis de documentos legales
--------------------------------------------
Define los modelos de datos para el análisis automático de documentos legales.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class TipoRiesgo(str, Enum):
    """Niveles de riesgo identificados en el documento"""
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"

class Clausula(BaseModel):
    """Modelo para una cláusula identificada en el documento"""
    titulo: str = Field(..., description="Título o descripción de la cláusula")
    contenido: str = Field(..., description="Contenido de la cláusula")
    pagina: Optional[int] = Field(None, description="Número de página donde se encontró")
    riesgo: Optional[TipoRiesgo] = Field(None, description="Nivel de riesgo identificado")
    razon_riesgo: Optional[str] = Field(None, description="Razón por la que se considera riesgosa")

class Riesgo(BaseModel):
    """Modelo para un riesgo identificado en el documento"""
    descripcion: str = Field(..., description="Descripción del riesgo identificado")
    nivel: TipoRiesgo = Field(..., description="Nivel de riesgo")
    clausulas_relacionadas: List[str] = Field(..., description="Títulos de las cláusulas relacionadas")
    recomendacion: str = Field(..., description="Recomendación para mitigar el riesgo")

class DocumentoCreate(BaseModel):
    """Modelo para crear un documento en el sistema"""
    title: str
    document_type: str
    reference_number: str
    issue_date: Optional[datetime] = None
    source: Optional[str] = None
    content: str
    keywords: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class DocumentoResponse(BaseModel):
    """Modelo para la respuesta del análisis de documento"""
    id: Optional[int] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    fecha_subida: Optional[datetime] = None
    estado: Optional[str] = None
    usuario_id: Optional[int] = None
    clausulas_destacadas: Optional[List[Clausula]] = None
    riesgos_detectados: Optional[List[Riesgo]] = None
    resumen_general: Optional[str] = None
    recomendaciones: Optional[List[str]] = None
    tipo_documento: Optional[str] = None
    fecha_documento: Optional[str] = None

class AnalisisResponse(BaseModel):
    """Modelo para la respuesta del análisis detallado de un documento"""
    documento_id: int = Field(..., description="ID del documento analizado")
    resultado: Dict[str, Any] = Field(..., description="Resultado del análisis en formato JSON")
    fecha_analisis: Optional[datetime] = Field(None, description="Fecha y hora del análisis") 