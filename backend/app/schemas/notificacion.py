from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.notificacion import TipoNotificacion

class NotificacionBase(BaseModel):
    tipo: TipoNotificacion
    titulo: str
    mensaje: str
    datos_adicionales: Optional[Dict[str, Any]] = None

class NotificacionCreate(NotificacionBase):
    usuario_id: int

class NotificacionResponse(NotificacionBase):
    id: int
    usuario_id: int
    leido: bool
    fecha_creacion: datetime
    fecha_lectura: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 