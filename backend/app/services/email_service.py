"""
Servicio de Correo Electrónico
--------------------------
Implementa la lógica para el envío de correos electrónicos.
"""

import os
from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dotenv import load_dotenv
from app.core.config import settings
import jinja2
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class EmailService:
    """Servicio para manejar el envío de correos electrónicos"""

    def __init__(self):
        """Inicializa el servicio de correo"""
        self.fastmail = None
        self.jinja_env = None
        self._initialized = False
        
        # Verificar si las variables de email están configuradas
        if self._email_vars_configured():
            self._initialize_email()
        else:
            logger.warning("⚠️ Variables de entorno de email no configuradas. EmailService deshabilitado.")

    def _email_vars_configured(self) -> bool:
        """Verifica si las variables de entorno de email están configuradas"""
        required_vars = [
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD, 
            settings.MAIL_FROM,
            settings.MAIL_SERVER
        ]
        # Verificar que todas las variables tengan valores válidos y no sean strings vacíos
        return all(var and var.strip() and "@" in str(var) if "MAIL_FROM" in str(var) else var and var.strip() for var in required_vars if var is not None)

    def _initialize_email(self):
        """Inicializa la configuración de email si las variables están disponibles"""
        try:
            # Doble verificación antes de crear ConnectionConfig
            if not settings.MAIL_FROM or "@" not in settings.MAIL_FROM:
                logger.warning("⚠️ MAIL_FROM no es una dirección de email válida")
                return
                
            if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
                logger.warning("⚠️ Credenciales de email incompletas")
                return
                
            self.config = ConnectionConfig(
                MAIL_USERNAME=settings.MAIL_USERNAME,
                MAIL_PASSWORD=settings.MAIL_PASSWORD,
                MAIL_FROM=settings.MAIL_FROM,
                MAIL_PORT=settings.MAIL_PORT,
                MAIL_SERVER=settings.MAIL_SERVER,
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True
            )
            
            self.fastmail = FastMail(self.config)
            self.jinja_env = Environment(
                loader=FileSystemLoader("app/templates/email")
            )
            self._initialized = True
            logger.info("✅ EmailService inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando EmailService: {e}")
            self.fastmail = None
            self.jinja_env = None
            self._initialized = False

    def _check_email_enabled(self):
        """Verifica si el servicio de email está habilitado"""
        if not self._initialized:
            raise Exception("Servicio de email no está configurado. Revisa las variables de entorno MAIL_*")

    async def enviar_correo_activacion(self, email: str, nombre: str, token: str) -> None:
        """
        Envía un correo de activación de cuenta.
        
        Args:
            email: Correo electrónico del destinatario
            nombre: Nombre del usuario
            token: Token de activación
        """
        self._check_email_enabled()
        
        template = self.jinja_env.get_template("activacion.html")
        url_activacion = f"http://{settings.HOST}:{settings.PORT}/activar-cuenta?token={token}"
        
        html = template.render(
            nombre=nombre,
            activacion_url=url_activacion,
            fecha=datetime.now().strftime("%d/%m/%Y")
        )
        
        message = MessageSchema(
            subject="Activa tu cuenta en LegalAssista",
            recipients=[email],
            body=html,
            subtype="html"
        )
        
        await self.fastmail.send_message(message)

    async def enviar_correo_recuperacion(self, email: str, token: str) -> None:
        """
        Envía un correo de recuperación de contraseña.
        
        Args:
            email: Correo electrónico del destinatario
            token: Token de recuperación
        """
        self._check_email_enabled()
        
        template = self.jinja_env.get_template("recuperacion.html")
        url_recuperacion = f"http://{settings.HOST}:{settings.PORT}/recuperar-password?token={token}"
        
        html = template.render(
            recuperacion_url=url_recuperacion,
            fecha=datetime.now().strftime("%d/%m/%Y")
        )
        
        message = MessageSchema(
            subject="Recupera tu contraseña en LegalAssista",
            recipients=[email],
            body=html,
            subtype="html"
        )
        
        await self.fastmail.send_message(message)

    async def enviar_notificacion(self, email: str, nombre: str, titulo: str, mensaje: str):
        """Envía una notificación por correo electrónico"""
        self._check_email_enabled()
        
        template = self.jinja_env.get_template("notificacion.html")
        frontend_url = f"http://{settings.HOST}:{settings.PORT}"
        
        html_content = template.render(
            nombre=nombre,
            titulo=titulo,
            mensaje=mensaje,
            fecha=datetime.now().strftime("%d/%m/%Y"),
            frontend_url=frontend_url
        )
        
        message = MessageSchema(
            subject=f"Notificación: {titulo}",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        await self.fastmail.send_message(message) 