#!/usr/bin/env python
"""
Script de Prueba para Consultas sobre Estabilidad Laboral Reforzada
------------------------------------------------------------------
Este script prueba múltiples consultas relacionadas con la estabilidad
laboral reforzada y derechos durante el embarazo usando el servicio BM25 optimizado.
"""

import requests
import json
import logging
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_estabilidad")

# Configuración
BASE_URL = "http://127.0.0.1:12345/api"
SEARCH_URL = f"{BASE_URL}/search-optimized/"

# Términos de búsqueda relacionados con estabilidad laboral y embarazo
SEARCH_TERMS = [
    "estabilidad laboral reforzada",
    "fuero de maternidad",
    "despido mujer embarazada",
    "protección trabajadora embarazada",
    "licencia maternidad",
    "reintegro trabajadora embarazada",
    "indemnización despido embarazo",
    "derechos mujer embarazada trabajo"
]

def print_document(doc, index=None):
    """Imprime información de un documento legal de forma legible"""
    prefix = f"\nDocumento {index}: " if index is not None else "\nDocumento: "
    print(f"{prefix}")
    print(f"  ID: {doc['document_id']}")
    print(f"  Título: {doc['title']}")
    print(f"  Tipo: {doc['document_type']}")
    print(f"  Referencia: {doc['reference_number']}")
    print(f"  Relevancia: {doc['relevance_score']:.3f}")
    print(f"  Fragmento: {doc['snippet']}")

def search_documents(query, limit=3):
    """Busca documentos utilizando la búsqueda optimizada BM25"""
    logger.info(f"Buscando documentos para: '{query}'")
    
    # Parámetros de la consulta
    params = {
        "query": query,
        "limit": limit
    }
    
    try:
        # Realizar la búsqueda
        response = requests.post(SEARCH_URL, params=params)
        response.raise_for_status()
        
        # Procesar la respuesta
        results = response.json()
        documents = results.get("results", [])
        cached = results.get("cached", False)
        processing_time = results.get("processing_time_ms", 0)
        
        logger.info(f"Búsqueda completada en {processing_time:.2f}ms, encontrados {len(documents)} documentos")
        logger.info(f"Resultado desde caché: {'Sí' if cached else 'No'}")
        
        return documents, processing_time, cached
    
    except Exception as e:
        logger.error(f"Error al buscar documentos: {str(e)}")
        return [], 0, False

def test_search_term(term, limit=3):
    """Prueba un término de búsqueda y muestra los resultados"""
    print("\n" + "-" * 80)
    print(f"TÉRMINO: '{term}'")
    print("-" * 80)
    
    documents, processing_time, cached = search_documents(term, limit)
    
    if documents:
        print(f"\nSe encontraron {len(documents)} documentos relevantes:")
        print(f"Tiempo de procesamiento: {processing_time:.2f}ms | Desde caché: {'Sí' if cached else 'No'}")
        
        for i, doc in enumerate(documents, 1):
            print_document(doc, i)
    else:
        print("\nNo se encontraron documentos relevantes.")
    
    return len(documents)

def get_index_status():
    """Obtiene el estado actual del índice BM25"""
    try:
        response = requests.get(f"{SEARCH_URL}status")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error al obtener estado del índice: {str(e)}")
        return {}

def main():
    """Función principal que ejecuta las pruebas"""
    print("\n" + "=" * 80)
    print("PRUEBA DE CONSULTAS SOBRE ESTABILIDAD LABORAL REFORZADA")
    print("=" * 80)
    
    # Verificar estado del índice BM25
    status = get_index_status()
    if status:
        print("\nEstado del índice BM25:")
        print(f"  Inicializado: {'Sí' if status.get('initialized', False) else 'No'}")
        print(f"  Documentos indexados: {status.get('document_count', 0)}")
        print(f"  Última actualización: {status.get('last_update', 'Desconocida')}")
        print(f"  Caché activado: {'Sí' if status.get('cache_enabled', False) else 'No'}")
    
    # Estadísticas generales
    total_results = 0
    total_searches = len(SEARCH_TERMS)
    start_time = time.time()
    
    # Probar cada término de búsqueda
    for term in SEARCH_TERMS:
        doc_count = test_search_term(term)
        total_results += doc_count
    
    # Mostrar estadísticas
    elapsed_time = time.time() - start_time
    avg_results = total_results / total_searches if total_searches > 0 else 0
    
    print("\n" + "=" * 80)
    print("RESULTADOS DE LA PRUEBA")
    print("=" * 80)
    print(f"Total de búsquedas realizadas: {total_searches}")
    print(f"Total de documentos encontrados: {total_results}")
    print(f"Promedio de documentos por búsqueda: {avg_results:.2f}")
    print(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")
    print("=" * 80)
    print(f"PRUEBA COMPLETADA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main() 