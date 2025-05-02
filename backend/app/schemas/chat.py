from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MensajeBase(BaseModel):
    contenido: str = Field(..., min_length=1, max_length=500)

class MensajeCreate(MensajeBase):
    receptor_id: int

class MensajeResponse(MensajeBase):
    id: int
    remitente_id: int
    receptor_id: int
    timestamp: datetime
    leido: bool

    class Config:
        orm_mode = True

class ConversacionResponse(BaseModel):
    id: int
    nombre: str
    ultimo_mensaje: Optional[str]
    timestamp: Optional[datetime]
    no_leidos: int
    online: bool

    class Config:
        orm_mode = True 