"""
Configuración centralizada
-----------------------
Configuración centralizada para el backend de AI Labor Law Assistant.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("config")

# Cargar variables de entorno
env_file = Path(__file__).resolve().parent / '.env'
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
    logger.info(f"Variables de entorno cargadas desde {env_file}")
else:
    logger.warning(f"Archivo .env no encontrado en {env_file}. Usando variables de entorno del sistema.")
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
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")  # Cambiado a gpt-3.5-turbo por defecto (más económico)

# Configuración de optimización de consumo de tokens
ECONOMY_MODE = os.getenv("ECONOMY_MODE", "True").lower() == "true"  # Activado por defecto
MAX_TOKENS_OUTPUT = int(os.getenv("MAX_TOKENS_OUTPUT", "150"))  # Límite de tokens en respuesta
MAX_DOCUMENTS = int(os.getenv("MAX_DOCUMENTS", "2"))  # Número máximo de documentos a incluir
MAX_CHARS_PER_DOC = int(os.getenv("MAX_CHARS_PER_DOC", "300"))  # Caracteres máximos por documento
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"  # Caché activado por defecto
DAILY_QUERY_LIMIT = int(os.getenv("DAILY_QUERY_LIMIT", "25"))  # Límite diario de consultas

# Directorio para almacenar caché
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Validación de la configuración de OpenAI
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here" or OPENAI_API_KEY == "sk-your-actual-openai-api-key":
    logger.warning(
        "⚠️ OPENAI_API_KEY no está configurada correctamente. "
        "Las llamadas a la API de OpenAI fallarán. "
        "Configura tu API key en el archivo .env"
    )

# Configuración de Twilio (para integración WhatsApp)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Función para validar la configuración
def validate_config():
    """Valida la configuración y emite advertencias si hay problemas"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here" or OPENAI_API_KEY == "sk-your-actual-openai-api-key":
        logger.error("❌ OPENAI_API_KEY no configurada. Las llamadas a la API de OpenAI fallarán.")
        return False
    
    if not OPENAI_API_KEY.startswith(("sk-", "org-")):
        logger.error("❌ OPENAI_API_KEY inválida. Debe comenzar con 'sk-' o 'org-'.")
        return False
    
    logger.info("✅ Configuración de OpenAI validada correctamente.")
    return True 