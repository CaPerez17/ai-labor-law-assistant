#!/usr/bin/env python3
"""
Script para probar el endpoint /api/ask/ del backend
Este script envía una consulta de prueba al endpoint y muestra la respuesta
"""

import requests
import json
import logging
import sys
import os

# Configuración de logging con nivel más detallado si DEBUG está habilitado
logging.basicConfig(
    level=logging.DEBUG if os.environ.get('DEBUG') == '1' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_api")

def test_ask_endpoint(query: str):
    """
    Prueba el endpoint /api/ask/ con una consulta específica
    
    Args:
        query: La consulta a enviar al endpoint
        
    Returns:
        bool: True si la prueba fue exitosa, False en caso contrario
    """
    url = "http://127.0.0.1:12345/api/ask/"
    
    # Datos para la solicitud
    payload = {
        "query": query
    }
    
    logger.info(f"🔍 Enviando consulta: '{query}'")
    logger.info(f"📌 URL: {url}")
    logger.debug(f"📦 Payload: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        # Realizar la solicitud POST con cabeceras explícitas
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        logger.debug(f"🔤 Headers: {headers}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # Verificar el código de estado
        logger.info(f"📊 Código de estado: {response.status_code}")
        logger.debug(f"🔤 Headers de respuesta: {dict(response.headers)}")
        
        if response.status_code != 200:
            logger.error(f"❌ Error: {response.status_code} - {response.text}")
            return False
        
        # Obtener y mostrar la respuesta
        try:
            data = response.json()
            logger.debug(f"📄 Respuesta JSON completa: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error decodificando JSON: {e}")
            logger.error(f"Respuesta recibida: {response.text[:1000]}")
            return False
        
        # Mostrar la respuesta formateada
        logger.info("✅ Respuesta recibida del servidor:")
        logger.info("-" * 80)
        
        if "response" in data:
            # Mostrar la respuesta general
            response_text = data["response"]
            logger.info(response_text[:800] + "..." if len(response_text) > 800 else response_text)
        
        if "references" in data:
            # Verificar si hay documentos relacionados
            if data["references"]:
                # Si hay referencias, mostrarlas
                logger.info("\n📚 Documentos relacionados:")
                for i, doc in enumerate(data["references"], 1):
                    logger.info(f"{i}. {doc.get('title', 'Sin título')} - Relevancia: {doc.get('relevance', 0)}")
            else:
                # Si references está vacío, buscamos referencias en el texto de la respuesta
                logger.debug("Lista de referencias vacía, verificando referencias en el texto de respuesta")
        
        logger.info("-" * 80)
        
        # Guardar respuesta completa en un archivo para análisis posterior
        with open("api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("💾 Respuesta completa guardada en 'api_response.json'")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        logger.error("❌ Error de conexión: No se pudo conectar al servidor. ¿Está el backend ejecutándose?")
        logger.debug(f"Detalle del error: {str(e)}")
        return False
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout: La solicitud tardó demasiado tiempo en completarse")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        logger.debug(f"Tipo de error: {type(e).__name__}", exc_info=True)
        return False

if __name__ == "__main__":
    # Consulta de prueba predeterminada
    default_query = "¿Cuántos días de vacaciones me corresponden por ley en Colombia?"
    
    # Usar la consulta proporcionada como argumento o la predeterminada
    query = sys.argv[1] if len(sys.argv) > 1 else default_query
    
    # Ejecutar la prueba
    logger.info("🚀 Iniciando prueba del endpoint /api/ask/")
    success = test_ask_endpoint(query)
    
    if success:
        logger.info("🎉 Prueba completada con éxito")
        sys.exit(0)
    else:
        logger.error("❌ La prueba falló")
        sys.exit(1) 