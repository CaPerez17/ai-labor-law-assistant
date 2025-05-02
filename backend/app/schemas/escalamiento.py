"""
Esquemas para el módulo de escalamiento a abogados
----------------------------------------------
Define los modelos de datos para el proceso de escalamiento
de casos a abogados humanos.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class NivelRiesgo(str, Enum):
    """Niveles de riesgo para escalamiento"""
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"

class EstadoEscalamiento(str, Enum):
    """Estados posibles del escalamiento"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    RECHAZADO = "rechazado"

class EscalamientoInput(BaseModel):
    """Modelo para la entrada del proceso de escalamiento"""
    usuario_id: str = Field(..., description="Identificador único del usuario")
    flujo: str = Field(..., description="Flujo o módulo donde se originó el escalamiento")
    detalle_consulta: str = Field(..., description="Detalle de la consulta o situación")
    nivel_riesgo: NivelRiesgo = Field(..., description="Nivel de riesgo identificado")
    contacto_whatsapp: Optional[str] = Field(None, description="Número de WhatsApp para contacto")

class EscalamientoResponse(BaseModel):
    """Modelo para la respuesta del proceso de escalamiento"""
    mensaje_confirmacion: str = Field(..., description="Mensaje de confirmación para el usuario")
    estado: EstadoEscalamiento = Field(..., description="Estado actual del escalamiento")
    caso_id: Optional[str] = Field(None, description="Identificador del caso en el CRM")
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora del escalamiento") 