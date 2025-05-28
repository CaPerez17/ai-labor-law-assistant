from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class MensajeBase(BaseModel):
    contenido: str = Field(..., min_length=1, max_length=500)

class MensajeCreate(BaseModel):
    receptor_id: int

class MensajeResponse(BaseModel):
    id: int
    remitente_id: int
    receptor_id: int
    timestamp: datetime
    leido: bool
    
    model_config = ConfigDict(from_attributes=True)

class ConversacionResponse(BaseModel):
    id: int
    nombre: str
    ultimo_mensaje: Optional[str] = None
    timestamp: Optional[datetime] = None
    no_leidos: int = 0
    online: bool = False
    
    model_config = ConfigDict(from_attributes=True) 