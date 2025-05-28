"""
Esquemas de Caso
--------------
Define los esquemas de Pydantic para la validación y serialización de casos.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class CasoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: str = Field(..., min_length=1)
    nivel_riesgo: Optional[str] = "MEDIO"

class CasoCreate(CasoBase):
    cliente_id: int
    abogado_id: Optional[int] = None

class CasoUpdate(BaseModel):
    estado: Optional[str] = None
    comentarios: Optional[str] = None
    abogado_id: Optional[int] = None

class CasoResponse(CasoBase):
    id: int
    estado: str
    comentarios: Optional[str] = None
    cliente_id: int
    abogado_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_cierre: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 