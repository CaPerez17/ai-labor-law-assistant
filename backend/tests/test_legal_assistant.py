#!/usr/bin/env python
"""
Test del Asistente Legal Integrado (BM25 + GPT)
------------------------------------------
Este script prueba la integración completa del sistema de búsqueda BM25
con GPT para generar respuestas a consultas legales con citas.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Asegurarnos de que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar módulos necesarios
from app.db.database import SessionLocal, engine
from app.schemas.legal_document import SearchQuery
from app.services.search_service import SearchService
from app.services.ai_service import AIService


def test_legal_assistant(query_text: str) -> Dict[str, Any]:
    """
    Prueba el asistente legal con una consulta específica.
    
    Args:
        query_text: Texto de la consulta legal
        
    Returns:
        Diccionario con la respuesta y metadatos
    """
    print(f"\n📝 Procesando consulta: '{query_text}'")
    start_time = time.time()
    
    try:
        # Inicializar servicios
        db = SessionLocal()
        search_service = SearchService()
        ai_service = AIService()
        
        # 1. Buscar documentos relevantes con BM25
        print("\n⏳ Buscando documentos relevantes con BM25...")
        search_time_start = time.time()
        
        search_query = SearchQuery(query=query_text, limit=5)
        search_results = search_service.search_documents(db, search_query)
        
        search_time = time.time() - search_time_start
        print(f"✅ Búsqueda completada en {search_time*1000:.2f}ms. Encontrados {len(search_results)} documentos relevantes.")
        
        if not search_results:
            print("❌ No se encontraron documentos relevantes para esta consulta.")
            return {
                "query": query_text,
                "error": "No se encontraron documentos relevantes",
                "timestamp": datetime.now().isoformat()
            }
        
        # Imprimir documentos encontrados
        print("\n📄 Documentos más relevantes:")
        for i, doc in enumerate(search_results[:3], 1):
            print(f"  {i}. {doc['title']} (Score: {doc['relevance_score']})")
            print(f"     Snippet: {doc['snippet'][:100]}...")
        
        # 2. Formatear contexto para GPT
        print("\n⏳ Formateando contexto para GPT...")
        context = ai_service.format_bm25_context(query_text, search_results)
        
        # 3. Generar respuesta con GPT
        print("\n⏳ Generando respuesta con GPT...")
        gpt_time_start = time.time()
        
        response_text, confidence_score, needs_human_review, review_reason = ai_service.generate_response(
            query_text=query_text,
            search_results=search_results,
            threshold=0.7
        )
        
        gpt_time = time.time() - gpt_time_start
        print(f"✅ Respuesta generada en {gpt_time:.2f} segundos.")
        print(f"📊 Puntuación de confianza: {confidence_score}")
        
        if needs_human_review:
            print(f"⚠️ Se requiere revisión humana: {review_reason}")
        
        # 4. Formatear respuesta final con fuentes
        formatted_response = ai_service.format_response_with_sources(response_text, search_results)
        
        # 5. Calcular tiempo total
        total_time = time.time() - start_time
        
        # Armar respuesta completa para retornar
        result = {
            "query": query_text,
            "response": response_text,
            "sources": formatted_response["sources"],
            "confidence_score": confidence_score,
            "needs_human_review": needs_human_review,
            "review_reason": review_reason,
            "performance": {
                "search_time_ms": round(search_time * 1000, 2),
                "gpt_time_ms": round(gpt_time * 1000, 2),
                "total_time_ms": round(total_time * 1000, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Cerrar sesión
        db.close()
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "query": query_text,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def print_result(result: Dict[str, Any]) -> None:
    """Imprime el resultado en formato legible"""
    print("\n" + "=" * 80)
    print(f"📋 RESULTADO PARA: '{result['query']}'")
    print("=" * 80)
    
    if "error" in result:
        print(f"\n❌ ERROR: {result['error']}")
        return
    
    print(f"\n✅ RESPUESTA:")
    print(f"{result['response']}")
    
    print("\n📚 FUENTES CITADAS:")
    for source in result.get("sources", []):
        print(f"  - {source['title']} (ID: {source['id']})")
    
    print("\n⚙️ MÉTRICAS:")
    print(f"  Confianza: {result['confidence_score']}")
    print(f"  Tiempo de búsqueda: {result['performance']['search_time_ms']} ms")
    print(f"  Tiempo de GPT: {result['performance']['gpt_time_ms']} ms")
    print(f"  Tiempo total: {result['performance']['total_time_ms']} ms")
    
    if result.get("needs_human_review"):
        print(f"\n⚠️ REQUIERE REVISIÓN HUMANA: {result.get('review_reason', 'No especificado')}")
    
    print("\n" + "=" * 80)


def run_test_suite():
    """Ejecuta una serie de pruebas con diferentes consultas legales"""
    # Lista de consultas de prueba representativas
    test_queries = [
        "¿Cuántos días de licencia de maternidad me corresponden por ley en Colombia?",
        "¿Cuál es el salario mínimo legal vigente en Colombia para 2023?",
        "¿Qué es la estabilidad laboral reforzada y a quiénes aplica?",
        "¿Cómo se calcula la indemnización por despido sin justa causa?",
        "¿Qué es el fuero de maternidad y cómo protege a las trabajadoras embarazadas?",
        "¿Cuáles son las justas causas para terminar un contrato laboral?"
    ]
    
    results = []
    
    for query in test_queries:
        result = test_legal_assistant(query)
        print_result(result)
        results.append(result)
        
        # Pequeña pausa para no exceder límites de API
        time.sleep(2)
    
    # Guardar resultados en archivo JSON
    output_file = os.path.join(backend_dir, "test_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Resultados guardados en {output_file}")


if __name__ == "__main__":
    print("=" * 80)
    print("✨ Prueba del Asistente Legal (BM25 + GPT) ✨")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        # Usar la consulta proporcionada como argumento
        query = " ".join(sys.argv[1:])
        result = test_legal_assistant(query)
        print_result(result)
    else:
        # Ejecutar suite de pruebas completa
        run_test_suite()
    
    print("\n✅ Pruebas completadas.") 