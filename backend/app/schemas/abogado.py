"""
Esquemas para el módulo de abogados
--------------------------------
Define los modelos de datos para la gestión de casos por abogados.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EstadoCaso(str, Enum):
    """Estados posibles para un caso"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"

class NivelRiesgo(str, Enum):
    """Niveles de riesgo para un caso"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

class CasoAbogado(BaseModel):
    """Modelo para un caso asignado a un abogado"""
    id_caso: str = Field(..., description="Identificador único del caso")
    usuario_id: str = Field(..., description="ID del usuario que reportó el caso")
    flujo: str = Field(..., description="Flujo del caso (ej: contrato, indemnización)")
    nivel_riesgo: NivelRiesgo = Field(..., description="Nivel de riesgo del caso")
    detalle_consulta: str = Field(..., description="Detalle de la consulta del usuario")
    estado: EstadoCaso = Field(default=EstadoCaso.PENDIENTE, description="Estado actual del caso")
    comentarios_abogado: List[str] = Field(default_factory=list, description="Comentarios del abogado")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de creación del caso")
    fecha_ultima_actualizacion: datetime = Field(default_factory=datetime.now, description="Fecha de última actualización")
    numero_whatsapp: Optional[str] = Field(None, description="Número de WhatsApp del usuario")

class UpdateCasoInput(BaseModel):
    """Modelo para actualizar un caso"""
    id_caso: str = Field(..., description="ID del caso a actualizar")
    nuevo_estado: EstadoCaso = Field(..., description="Nuevo estado del caso")
    comentarios: str = Field(..., description="Nuevos comentarios del abogado")
    
    @validator('comentarios')
    def validar_comentarios(cls, v):
        """Valida la longitud de los comentarios"""
        if len(v) > 1000:
            raise ValueError('Los comentarios no pueden exceder los 1000 caracteres')
        return v

class CasoResponse(BaseModel):
    """Modelo para la respuesta de operaciones con casos"""
    exito: bool = Field(..., description="Indica si la operación fue exitosa")
    mensaje: str = Field(..., description="Mensaje de confirmación o error")
    caso: Optional[CasoAbogado] = Field(None, description="Datos del caso (si aplica)") 