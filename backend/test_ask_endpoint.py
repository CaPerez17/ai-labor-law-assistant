#!/usr/bin/env python
"""
Test del Endpoint /api/ask/
------------------------
Este script prueba el nuevo endpoint para consultas legales directas.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import Dict, Any

# Asegurarnos de que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# URL base del servidor local
BASE_URL = "http://127.0.0.1:12345/api"

def test_ask_endpoint(query: str) -> Dict[str, Any]:
    """
    Envía una consulta al endpoint /api/ask/ y devuelve la respuesta.
    
    Args:
        query: Texto de la consulta legal
        
    Returns:
        Respuesta del servidor como diccionario
    """
    print(f"\n📝 Enviando consulta: '{query}'")
    
    url = f"{BASE_URL}/ask/"
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        request_time = time.time() - start_time
        
        print(f"⏱️ Tiempo de respuesta de la API: {request_time:.2f} segundos")
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ Error: Código {response.status_code}")
            print(f"Respuesta: {response.text}")
            return {
                "error": f"Error al consultar la API: {response.status_code}",
                "detail": response.text
            }
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"error": str(e)}


def print_result(result: Dict[str, Any]) -> None:
    """Imprime el resultado en formato legible"""
    print("\n" + "=" * 80)
    print(f"📋 RESPUESTA PARA: '{result.get('query', 'N/A')}'")
    print("=" * 80)
    
    if "error" in result:
        print(f"\n❌ ERROR: {result['error']}")
        return
    
    print(f"\n✅ RESPUESTA:")
    print(f"{result['response']}")
    
    print("\n📚 REFERENCIAS LEGALES:")
    for ref in result.get("references", []):
        print(f"  - {ref['title']} (ID: {ref['id']}, Relevancia: {ref['relevance']})")
    
    print("\n⚙️ MÉTRICAS:")
    print(f"  Confianza: {result.get('confidence_score', 'N/A')}")
    print(f"  Tiempo de procesamiento: {result.get('processing_time_ms', 'N/A')} ms")
    
    if result.get("needs_human_review"):
        print(f"\n⚠️ REQUIERE REVISIÓN HUMANA: {result.get('review_reason', 'No especificado')}")
    
    print("\n" + "=" * 80)


def run_test_suite():
    """Ejecuta una serie de pruebas con diferentes consultas legales"""
    # Lista de consultas de prueba representativas
    test_queries = [
        "¿Cuántos días de licencia de maternidad me corresponden por ley en Colombia?",
        "¿Qué es la estabilidad laboral reforzada?",
        "¿Cómo se calcula la indemnización por despido sin justa causa?"
    ]
    
    results = []
    
    for query in test_queries:
        result = test_ask_endpoint(query)
        print_result(result)
        results.append(result)
        
        # Pequeña pausa para no saturar el servidor
        time.sleep(1)
    
    # Guardar resultados en archivo JSON
    output_file = os.path.join(backend_dir, "ask_test_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Resultados guardados en {output_file}")


if __name__ == "__main__":
    print("=" * 80)
    print("✨ Prueba del Endpoint de Consultas Legales Directas (/api/ask/) ✨")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        # Usar la consulta proporcionada como argumento
        query = " ".join(sys.argv[1:])
        result = test_ask_endpoint(query)
        print_result(result)
    else:
        # Ejecutar suite de pruebas completa
        run_test_suite()
    
    print("\n✅ Pruebas completadas.") 