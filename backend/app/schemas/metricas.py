"""
Esquemas para el módulo de métricas y feedback
------------------------------------------
Define los modelos de datos para el registro de métricas de uso
y el feedback de los usuarios.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class MetricaUso(BaseModel):
    """Modelo para el registro de métricas de uso"""
    endpoint_accedido: str = Field(..., description="Endpoint o flujo accedido")
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora del acceso")
    duracion: float = Field(..., description="Duración de la interacción en segundos")
    exito: bool = Field(..., description="Indica si la interacción fue exitosa")
    usuario_id: Optional[str] = Field(None, description="Identificador del usuario (opcional)")
    detalles: Optional[dict] = Field(None, description="Detalles adicionales de la interacción")

class FeedbackUsuario(BaseModel):
    """Modelo para el feedback de los usuarios"""
    usuario_id: str = Field(..., description="Identificador del usuario")
    flujo: str = Field(..., description="Flujo o módulo evaluado")
    calificacion: int = Field(..., description="Calificación del 1 al 5")
    comentario: Optional[str] = Field(None, description="Comentario opcional del usuario")
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora del feedback")

    @validator('calificacion')
    def validar_calificacion(cls, v):
        """Valida que la calificación esté entre 1 y 5"""
        if not 1 <= v <= 5:
            raise ValueError('La calificación debe estar entre 1 y 5')
        return v

    @validator('comentario')
    def validar_comentario(cls, v):
        """Valida la longitud del comentario"""
        if v and len(v) > 500:
            raise ValueError('El comentario no puede exceder los 500 caracteres')
        return v

class FeedbackResponse(BaseModel):
    """Modelo para la respuesta del feedback"""
    mensaje: str = Field(..., description="Mensaje de confirmación")
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora de la respuesta") 