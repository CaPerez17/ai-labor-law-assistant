#!/usr/bin/env python3
"""
Test simple de conexión a OpenAI
Este script hace una prueba básica de conexión a la API de OpenAI
"""

import os
import sys
import logging
from openai import OpenAI
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_simple_openai")

# Cargar la API key desde .env
try:
    from dotenv import load_dotenv
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Variables de entorno cargadas desde {env_path.resolve()}")
except Exception as e:
    logger.warning(f"No se pudo cargar el archivo .env: {str(e)}")

def test_openai_connection():
    """Prueba una conexión simple a OpenAI"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY no está configurada")
        return False
        
    # Verificar formato de API key
    if not (api_key.startswith("sk-") and len(api_key) > 20):
        logger.warning(f"⚠️ Formato de OPENAI_API_KEY inusual: {api_key[:5]}***")
    else:
        logger.info("✅ Formato de OPENAI_API_KEY parece correcto")
    
    # Intentar conectar con OpenAI
    try:
        client = OpenAI(api_key=api_key)
        logger.info("✅ Cliente OpenAI inicializado")
        
        # Realizar una consulta simple
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": "Hola, dime la fecha actual."}
            ],
            max_tokens=50
        )
        
        logger.info(f"✅ Respuesta recibida: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al conectar con OpenAI: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🔄 Iniciando prueba de conexión con OpenAI...")
    success = test_openai_connection()
    
    if success:
        logger.info("✅ Prueba completada con éxito")
        sys.exit(0)
    else:
        logger.error("❌ Prueba fallida")
        sys.exit(1) 