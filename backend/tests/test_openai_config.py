#!/usr/bin/env python
"""
Script para verificar la configuración de OpenAI

Este script realiza pruebas para verificar:
1. La configuración correcta de OpenAI API Key
2. La inicialización del servicio AI
3. La validación de la API Key
4. Una prueba simple de generación
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_openai")

# Asegurar que el directorio backend esté en el path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar después de configurar el path
try:
    from config import OPENAI_API_KEY, GPT_MODEL, validate_config
    from app.services.ai_service import AIService
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.error("Asegúrate de estar ejecutando el script desde el directorio backend/")
    sys.exit(1)

def test_config_validation():
    """Prueba la validación de configuración"""
    logger.info("🔍 Verificando configuración de OpenAI...")
    
    result = validate_config()
    
    if result:
        logger.info("✅ Configuración de OpenAI validada exitosamente")
    else:
        logger.error("❌ Error en la configuración de OpenAI")
        logger.info("Revisa los valores en tu archivo .env")
        return False
    
    return True

def test_ai_service():
    """Prueba la inicialización del servicio de IA"""
    logger.info("🔍 Probando la inicialización del servicio de IA...")
    
    try:
        service = AIService()
        logger.info(f"✅ AIService inicializado con modelo: {service.model}")
        return service
    except Exception as e:
        logger.error(f"❌ Error al inicializar AIService: {str(e)}")
        return None

def test_api_key_validation(service):
    """Prueba la validación de la API key"""
    if not service:
        logger.error("❌ No se puede probar la API key sin servicio inicializado")
        return False
        
    logger.info("🔍 Verificando validez de la API key...")
    
    try:
        is_valid = service.is_api_key_valid()
        if is_valid:
            logger.info("✅ API key válida y funcional")
            return True
        else:
            logger.error("❌ API key inválida o expirada")
            return False
    except Exception as e:
        logger.error(f"❌ Error al validar la API key: {str(e)}")
        return False

def test_simple_completion(service):
    """Prueba una generación simple para verificar funcionamiento completo"""
    if not service:
        logger.error("❌ No se puede probar la generación sin servicio inicializado")
        return False
        
    logger.info("🔍 Probando generación simple con OpenAI...")
    
    try:
        prompt = "Saluda en español"
        system_message = "Eres un asistente amigable. Responde brevemente."
        
        response_text, error = service.generate_gpt_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=50,
            temperature=0.5
        )
        
        if error:
            logger.error(f"❌ Error en generación: {error}")
            return False
            
        logger.info(f"✅ Generación exitosa: '{response_text}'")
        return True
    except Exception as e:
        logger.error(f"❌ Error en test de generación: {str(e)}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas y reporta el resultado general"""
    logger.info("🔧 Iniciando pruebas de configuración de OpenAI")
    logger.info("-" * 60)
    
    tests_results = []
    
    # Prueba 1: Validación de configuración
    config_valid = test_config_validation()
    tests_results.append(("Validación de configuración", config_valid))
    
    if not config_valid:
        logger.warning("⚠️ La validación de configuración falló, las siguientes pruebas pueden fallar también")
    
    # Prueba 2: Inicialización del servicio
    service = test_ai_service()
    service_init = service is not None
    tests_results.append(("Inicialización del servicio", service_init))
    
    if not service_init:
        logger.error("❌ No se pudo inicializar el servicio, cancelando pruebas restantes")
        summarize_results(tests_results)
        return False
    
    # Prueba 3: Validación de API key
    api_key_valid = test_api_key_validation(service)
    tests_results.append(("Validación de API key", api_key_valid))
    
    if not api_key_valid:
        logger.error("❌ La API key no es válida, cancelando prueba de generación")
        summarize_results(tests_results)
        return False
    
    # Prueba 4: Generación simple
    generation_ok = test_simple_completion(service)
    tests_results.append(("Generación simple", generation_ok))
    
    # Resumen final
    return summarize_results(tests_results)

def summarize_results(results):
    """Muestra un resumen de los resultados de las pruebas"""
    logger.info("\n" + "-" * 60)
    logger.info("📋 RESUMEN DE PRUEBAS")
    logger.info("-" * 60)
    
    all_passed = True
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        if not result:
            all_passed = False
        logger.info(f"{status} - {name}")
    
    logger.info("-" * 60)
    
    if all_passed:
        logger.info("🎉 ¡Todas las pruebas pasaron! OpenAI está configurado correctamente.")
    else:
        logger.info("⚠️ Algunas pruebas fallaron. Revisa los errores y ajusta la configuración.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 