from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr
from typing import Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Labor Law Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de la base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Configuración de JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # Configuración de correo
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # Configuración de MercadoPago
    MERCADOPAGO_PUBLIC_KEY: str = os.getenv("MERCADOPAGO_PUBLIC_KEY", "")
    MERCADOPAGO_ACCESS_TOKEN: str = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    
    # Configuración de OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = os.environ.get("GPT_MODEL", "gpt-3.5-turbo")
    
    # Configuración del servidor
    HOST: str = os.environ.get("HOST", "0.0.0.0")  # Cambiado a 0.0.0.0 para Docker
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # URL del frontend para redirecciones
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Configuración de Redis para WebSockets y caché
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Configuración de la aplicación
    ECONOMY_MODE: bool = os.environ.get("ECONOMY_MODE", "True").lower() == "true"
    MAX_TOKENS_OUTPUT: int = int(os.environ.get("MAX_TOKENS_OUTPUT", "150"))
    MAX_DOCUMENTS: int = int(os.environ.get("MAX_DOCUMENTS", "2"))
    MAX_CHARS_PER_DOC: int = int(os.environ.get("MAX_CHARS_PER_DOC", "300"))
    ENABLE_CACHE: bool = os.environ.get("ENABLE_CACHE", "True").lower() == "true"
    DAILY_QUERY_LIMIT: int = int(os.getenv("DAILY_QUERY_LIMIT", "50"))
    
    # Configuración de WhatsApp
    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
    
    model_config = ConfigDict(env_file=".env", extra='ignore')

settings = Settings() 