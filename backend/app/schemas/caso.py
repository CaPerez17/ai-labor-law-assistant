"""
Esquemas de Caso
--------------
Define los esquemas de Pydantic para la validación y serialización de casos.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.caso import EstadoCaso

class CasoBase(BaseModel):
    titulo: str
    descripcion: str
    estado: EstadoCaso = EstadoCaso.ABIERTO

class CasoCreate(CasoBase):
    pass

class CasoResponse(CasoBase):
    id: int
    usuario_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True) 