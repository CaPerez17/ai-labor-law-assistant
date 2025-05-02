from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "LegalAssista"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de la base de datos
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./legalassista.db")
    
    # Configuración de JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "tu_clave_secreta_aqui")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de correo
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME", "test@example.com")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD", "test_password")
    MAIL_FROM: EmailStr = os.environ.get("MAIL_FROM", "test@example.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    
    # Configuración de MercadoPago
    MERCADOPAGO_PUBLIC_KEY: str = os.environ.get("MERCADOPAGO_PUBLIC_KEY", "")
    MERCADOPAGO_ACCESS_TOKEN: str = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "")
    
    # Configuración de OpenAI
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    GPT_MODEL: str = os.environ.get("GPT_MODEL", "gpt-3.5-turbo")
    
    # Configuración del servidor
    HOST: str = os.environ.get("HOST", "0.0.0.0")  # Cambiado a 0.0.0.0 para Docker
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # URL del frontend para redirecciones
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    
    # Configuración de Redis para WebSockets y caché
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    # Configuración de la aplicación
    ECONOMY_MODE: bool = os.environ.get("ECONOMY_MODE", "True").lower() == "true"
    MAX_TOKENS_OUTPUT: int = int(os.environ.get("MAX_TOKENS_OUTPUT", "150"))
    MAX_DOCUMENTS: int = int(os.environ.get("MAX_DOCUMENTS", "2"))
    MAX_CHARS_PER_DOC: int = int(os.environ.get("MAX_CHARS_PER_DOC", "300"))
    ENABLE_CACHE: bool = os.environ.get("ENABLE_CACHE", "True").lower() == "true"
    DAILY_QUERY_LIMIT: int = int(os.environ.get("DAILY_QUERY_LIMIT", "25"))
    
    # Configuración de WhatsApp
    WHATSAPP_API_URL: str = os.environ.get("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0")
    WHATSAPP_API_TOKEN: str = os.environ.get("WHATSAPP_API_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
    
    model_config = ConfigDict(env_file=".env")

settings = Settings() 