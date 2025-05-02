"""
Servicio de WhatsApp
-----------------
Implementa la lógica para enviar mensajes a través de WhatsApp Business API.
"""

import os
import logging
import httpx
from typing import Optional
from datetime import datetime

from app.schemas.whatsapp import WhatsappInput, WhatsappResponse

# Configurar logging
logger = logging.getLogger(__name__)

class WhatsappService:
    """Servicio para el envío de mensajes por WhatsApp"""
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria"""
        self.api_url = os.getenv("WHATSAPP_API_URL")
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        
        if not all([self.api_url, self.api_token, self.phone_number_id]):
            logger.warning("Faltan variables de entorno para WhatsApp")
    
    async def enviar_mensaje(self, data: WhatsappInput) -> WhatsappResponse:
        """
        Envía un mensaje por WhatsApp
        
        Args:
            data: Datos del mensaje a enviar
            
        Returns:
            Respuesta con el resultado del envío
        """
        if not all([self.api_url, self.api_token, self.phone_number_id]):
            return WhatsappResponse(
                exito=False,
                mensaje="Error: Configuración de WhatsApp incompleta"
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": data.numero_whatsapp,
            "type": "text",
            "text": {
                "body": data.mensaje_resumen
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"Mensaje enviado exitosamente a {data.numero_whatsapp}")
                    return WhatsappResponse(
                        exito=True,
                        mensaje="Mensaje enviado exitosamente",
                        id_mensaje=response_data.get("messages", [{}])[0].get("id")
                    )
                else:
                    error_msg = f"Error al enviar mensaje: {response.text}"
                    logger.error(error_msg)
                    return WhatsappResponse(
                        exito=False,
                        mensaje=error_msg
                    )
                    
        except httpx.TimeoutException:
            error_msg = "Timeout al conectar con WhatsApp API"
            logger.error(error_msg)
            return WhatsappResponse(
                exito=False,
                mensaje=error_msg
            )
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg)
            return WhatsappResponse(
                exito=False,
                mensaje=error_msg
            ) 