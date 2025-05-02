"""
Esquemas para el onboarding conversacional
---------------------------------------
Define los modelos de datos para el proceso de onboarding y clasificación
de necesidades del usuario.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TipoFlujo(str, Enum):
    """Tipos de flujos disponibles en el sistema"""
    CONTRATO_REALIDAD = "contrato_realidad"
    INDEMNIZACION = "indemnizacion"
    CONTRATO = "contrato"
    ANALISIS_DOCUMENTO = "analisis_documento"
    CONSULTA_GENERAL = "consulta_general"

class OnboardingInput(BaseModel):
    """Modelo para la entrada del proceso de onboarding"""
    free_text: str = Field(..., description="Texto libre con la consulta del usuario")

class OnboardingResponse(BaseModel):
    """Modelo para la respuesta del proceso de onboarding"""
    flujo_recomendado: TipoFlujo = Field(..., description="Flujo recomendado para el usuario")
    mensaje_bienvenida: str = Field(..., description="Mensaje de bienvenida personalizado")
    pasos_sugeridos: List[str] = Field(..., description="Lista de pasos sugeridos para el usuario")
    razon_recomendacion: Optional[str] = Field(None, description="Razón por la que se recomienda este flujo")
    necesita_abogado: bool = Field(False, description="Indica si se recomienda consultar con un abogado") 