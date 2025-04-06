#!/usr/bin/env python3
"""
Script para probar el endpoint /api/ask/ con una consulta sobre despido durante embarazo
"""

import requests
import json
import logging
import sys
import os
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_embarazo")

def test_ask_endpoint(query: str, output_file: str):
    """
    Prueba el endpoint /api/ask/ con una consulta específica
    
    Args:
        query: La consulta a enviar al endpoint
        output_file: Archivo donde guardar la respuesta
        
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
    
    try:
        # Realizar la solicitud POST
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # Verificar el código de estado
        logger.info(f"📊 Código de estado: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"❌ Error: {response.status_code} - {response.text}")
            return False
        
        # Obtener y mostrar la respuesta
        try:
            data = response.json()
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
            logger.info(response_text)
        
        if "references" in data and data["references"]:
            # Si hay referencias, mostrarlas
            logger.info("\n📚 Documentos relacionados:")
            for i, doc in enumerate(data["references"], 1):
                logger.info(f"{i}. {doc.get('title', 'Sin título')} - Relevancia: {doc.get('relevance', 0)}")
        
        logger.info("-" * 80)
        
        # Guardar respuesta completa en un archivo para análisis posterior
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Respuesta completa guardada en '{output_file}'")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        logger.error("❌ Error de conexión: No se pudo conectar al servidor. ¿Está el backend ejecutándose?")
        return False
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout: La solicitud tardó demasiado tiempo en completarse")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    # Consulta específica sobre despido durante embarazo
    query = """
    Soy una mujer de 30 años, me encuentro laborando con una empresa y me enteré hace poco 
    que estaba en embarazo. Fui despedida después de informar a mi jefe. ¿Qué derechos tengo?
    """
    
    # Nombre del archivo de salida con timestamp para evitar sobrescribir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"embarazo_response_{timestamp}.json"
    
    # Ejecutar la prueba
    logger.info("🚀 Iniciando prueba del endpoint /api/ask/ para caso de embarazo")
    success = test_ask_endpoint(query, output_file)
    
    if success:
        logger.info("🎉 Prueba completada con éxito")
        sys.exit(0)
    else:
        logger.error("❌ La prueba falló")
        sys.exit(1) 