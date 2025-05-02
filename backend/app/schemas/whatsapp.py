"""
Esquemas para el módulo de WhatsApp
--------------------------------
Define los modelos de datos para el envío de mensajes por WhatsApp.
"""

from pydantic import BaseModel, Field, validator
import re

class WhatsappInput(BaseModel):
    """Modelo para el envío de mensajes por WhatsApp"""
    numero_whatsapp: str = Field(..., description="Número de WhatsApp del destinatario")
    mensaje_resumen: str = Field(..., description="Resumen del caso a enviar")
    
    @validator('numero_whatsapp')
    def validar_numero(cls, v):
        """Valida el formato del número de WhatsApp"""
        if not re.match(r'^\+57\d{10}$', v):
            raise ValueError('El número debe tener el formato +57XXXXXXXXXX')
        return v
    
    @validator('mensaje_resumen')
    def validar_mensaje(cls, v):
        """Valida la longitud del mensaje"""
        if len(v) > 500:
            raise ValueError('El mensaje no puede exceder los 500 caracteres')
        return v

class WhatsappResponse(BaseModel):
    """Modelo para la respuesta del envío de WhatsApp"""
    exito: bool = Field(..., description="Indica si el mensaje se envió correctamente")
    mensaje: str = Field(..., description="Mensaje de confirmación o error")
    id_mensaje: str = Field(None, description="ID del mensaje en WhatsApp (si aplica)") 