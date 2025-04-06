#!/usr/bin/env python
"""
Script de Prueba para Consulta sobre Despido durante Embarazo
------------------------------------------------------------
Este script prueba la integración entre la búsqueda BM25 optimizada y 
el endpoint de respuesta para un caso real: despido durante embarazo.
"""

import requests
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_consulta")

# Configuración
BASE_URL = "http://127.0.0.1:12345/api"
SEARCH_URL = f"{BASE_URL}/search-optimized/"
ASK_URL = f"{BASE_URL}/ask/"

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

def search_relevant_documents(query, limit=5):
    """Busca documentos relevantes utilizando la búsqueda optimizada BM25"""
    logger.info(f"Buscando documentos relevantes para: '{query}'")
    
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
        
        return documents
    
    except Exception as e:
        logger.error(f"Error al buscar documentos: {str(e)}")
        return []

def ask_legal_question(query):
    """Realiza una consulta legal al endpoint ask"""
    logger.info(f"Enviando consulta legal: '{query}'")
    
    # Datos de la consulta
    payload = {
        "query": query
    }
    
    try:
        # Realizar la consulta
        response = requests.post(ASK_URL, json=payload)
        response.raise_for_status()
        
        # Procesar la respuesta
        result = response.json()
        return result
    
    except Exception as e:
        logger.error(f"Error al realizar consulta legal: {str(e)}")
        return None

def main():
    """Función principal que ejecuta las pruebas"""
    print("\n" + "=" * 80)
    print("PRUEBA DE CONSULTA: DESPIDO DURANTE EMBARAZO")
    print("=" * 80)
    
    # La consulta a realizar
    query = """Soy una mujer 30 años, me encuentro laborando con aliados integrales, 
    me enteré hace poco que me encontraba en embarazo y fui despedida, que puedo hacer?"""
    
    print(f"\nConsulta: {query}")
    print("\n" + "-" * 80)
    
    # 1. Buscar documentos relevantes con BM25 optimizado
    print("\nPASO 1: Búsqueda de documentos relevantes con BM25 optimizado")
    documents = search_relevant_documents(query, limit=3)
    
    if documents:
        print(f"\nSe encontraron {len(documents)} documentos relevantes:")
        for i, doc in enumerate(documents, 1):
            print_document(doc, i)
    else:
        print("\nNo se encontraron documentos relevantes.")
    
    print("\n" + "-" * 80)
    
    # 2. Realizar la consulta legal completa
    print("\nPASO 2: Consulta legal completa")
    legal_response = ask_legal_question(query)
    
    if legal_response:
        print("\nRespuesta legal:")
        print(f"\n{legal_response.get('response', 'No se obtuvo respuesta')}")
        
        print("\nNivel de confianza:", legal_response.get("confidence_score", 0))
        print("Requiere revisión humana:", "Sí" if legal_response.get("needs_human_review", False) else "No")
        
        if legal_response.get("needs_human_review", False):
            print("Motivo:", legal_response.get("review_reason", "No especificado"))
        
        print("\nTiempo de procesamiento:", f"{legal_response.get('processing_time_ms', 0):.2f}ms")
        
        references = legal_response.get("references", [])
        if references:
            print("\nReferencias legales:")
            for i, ref in enumerate(references, 1):
                print(f"  {i}. {ref}")
    else:
        print("\nNo se pudo obtener una respuesta legal.")
    
    print("\n" + "=" * 80)
    print(f"PRUEBA COMPLETADA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main() 