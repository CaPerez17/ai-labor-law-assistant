"""
Esquemas para el análisis de documentos legales
--------------------------------------------
Define los modelos de datos para el análisis automático de documentos legales.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

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

class DocumentoResponse(BaseModel):
    """Modelo para la respuesta del análisis de documento"""
    clausulas_destacadas: List[Clausula] = Field(..., description="Cláusulas importantes identificadas")
    riesgos_detectados: List[Riesgo] = Field(..., description="Riesgos identificados en el documento")
    resumen_general: str = Field(..., description="Resumen del contenido del documento")
    recomendaciones: List[str] = Field(..., description="Recomendaciones generales")
    tipo_documento: Optional[str] = Field(None, description="Tipo de documento identificado")
    fecha_documento: Optional[str] = Field(None, description="Fecha del documento si se puede identificar") 