"""
Configuración centralizada
-----------------------
Configuración centralizada para el backend de AI Labor Law Assistant.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base
BASE_DIR = Path(__file__).resolve().parent

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Configuración del servidor
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 12345))  # Puerto alto no común
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Configuración de OpenAI/LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")

# Configuración de Twilio (para integración WhatsApp)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "") 