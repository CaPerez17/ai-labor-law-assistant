#!/usr/bin/env python
"""
Test de Rendimiento de Búsqueda BM25 Optimizada
-------------------------------------------
Este script prueba el rendimiento de la búsqueda BM25 optimizada con parámetros ajustados
y sistema de caché de consultas.
"""

import os
import sys
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any

# Asegurarnos de que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar módulos necesarios
from app.db.database import SessionLocal, engine
from app.schemas.legal_document import SearchQuery
from app.services.search_service import SearchService


def test_search(query: str, k1: float = 1.5, b: float = 0.75, use_cache: bool = True) -> Dict[str, Any]:
    """
    Realiza una búsqueda y retorna los resultados y métricas de rendimiento.
    
    Args:
        query: Consulta a buscar
        k1: Parámetro k1 de BM25
        b: Parámetro b de BM25
        use_cache: Si se debe usar el caché
        
    Returns:
        Diccionario con resultados y métricas
    """
    try:
        # Crear una sesión de base de datos
        db = SessionLocal()
        
        # Inicializar el servicio de búsqueda con los parámetros especificados
        search_service = SearchService(k1=k1, b=b, use_cache=use_cache)
        
        # Crear objeto de consulta
        search_query = SearchQuery(query=query, limit=5)
        
        # Medir tiempo de ejecución
        start_time = time.time()
        
        # Realizar la búsqueda
        results = search_service.search_documents(db, search_query)
        
        # Calcular tiempo de ejecución
        execution_time = time.time() - start_time
        
        # Verificar si la respuesta proviene del caché
        is_cached = any(result.get("cached", False) for result in results)
        
        # Formatear respuesta
        response = {
            "query": query,
            "cached": is_cached,
            "results": results,
            "execution_time_ms": round(execution_time * 1000, 2),
            "result_count": len(results),
            "parameters": {
                "k1": k1,
                "b": b,
                "use_cache": use_cache
            }
        }
        
        # Cerrar sesión
        db.close()
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error al realizar la búsqueda: {e}")
        db.close()
        return {
            "query": query,
            "error": str(e),
            "execution_time_ms": 0,
            "result_count": 0
        }


def print_search_result(result: Dict[str, Any]) -> None:
    """Imprime el resultado de una búsqueda de forma legible"""
    print("\n" + "=" * 80)
    print(f"📝 Consulta: '{result['query']}'")
    print(f"⏱️  Tiempo de ejecución: {result['execution_time_ms']} ms")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
        
    print(f"🔢 Resultados: {result['result_count']}")
    print(f"🔄 Caché: {'✅ Sí' if result.get('cached', False) else '❌ No'}")
    print(f"⚙️  Parámetros: k1={result['parameters']['k1']}, b={result['parameters']['b']}")
    
    print("\n📋 Top resultados:")
    for i, doc in enumerate(result["results"][:3], 1):
        print(f"\n{i}. {doc['title']} (Score: {doc['relevance_score']})")
        print(f"   Tipo: {doc['document_type']}, ID: {doc['document_id']}")
        print(f"   Snippet: {doc['snippet'][:100]}...")
    
    print("=" * 80)


def benchmark_parameters() -> None:
    """Compara diferentes combinaciones de parámetros BM25"""
    print("\n🔍 Benchmark de parámetros BM25")
    
    # Consultas de prueba
    queries = [
        "¿Cuántos días de licencia de maternidad me corresponden?",
        "¿Cuál es el salario mínimo en Colombia?",
        "¿Qué es el fuero de estabilidad laboral reforzada?"
    ]
    
    # Combinaciones de parámetros a probar
    parameter_sets = [
        {"k1": 1.2, "b": 0.75},  # Valores originales
        {"k1": 1.5, "b": 0.75},  # Valores recomendados
        {"k1": 1.8, "b": 0.8},   # Mayor importancia a frecuencia
        {"k1": 1.3, "b": 0.6}    # Menor importancia a longitud
    ]
    
    # Ejecutar búsquedas con cada combinación
    results = []
    
    for params in parameter_sets:
        print(f"\n⚙️  Probando parámetros: k1={params['k1']}, b={params['b']}")
        
        param_results = []
        for query in queries:
            # Deshabilitar caché para benchmarking de parámetros
            result = test_search(query, k1=params['k1'], b=params['b'], use_cache=False)
            param_results.append(result)
            
            # Mostrar resultado
            print(f"  ✓ '{query}': {result['execution_time_ms']} ms, {result['result_count']} resultados")
            
        # Calcular promedio
        avg_time = statistics.mean([r['execution_time_ms'] for r in param_results])
        avg_results = statistics.mean([r['result_count'] for r in param_results])
        
        results.append({
            "parameters": params,
            "avg_time_ms": round(avg_time, 2),
            "avg_result_count": round(avg_results, 2)
        })
    
    # Mostrar resumen
    print("\n📊 Resumen de resultados:")
    for res in results:
        print(f"  k1={res['parameters']['k1']}, b={res['parameters']['b']}: {res['avg_time_ms']} ms, {res['avg_result_count']} resultados promedio")


def test_cache_performance() -> None:
    """Prueba el rendimiento del sistema de caché"""
    print("\n🔄 Prueba de rendimiento del caché")
    
    # Consultas para probar (varias veces la misma para ver efecto del caché)
    query = "¿Cuántos días de licencia de maternidad me corresponden?"
    
    # Primera ejecución (sin caché)
    print("\n📝 Primera ejecución (sin caché):")
    result1 = test_search(query, use_cache=True)
    print_search_result(result1)
    
    # Segunda ejecución (debería usar caché)
    print("\n📝 Segunda ejecución (con caché):")
    result2 = test_search(query, use_cache=True)
    print_search_result(result2)
    
    # Tercera ejecución (con caché)
    print("\n📝 Tercera ejecución (con caché):")
    result3 = test_search(query, use_cache=True)
    print_search_result(result3)
    
    # Comparar rendimiento
    if result1["execution_time_ms"] > 0 and result2["execution_time_ms"] > 0:
        speedup = result1["execution_time_ms"] / result2["execution_time_ms"]
        print(f"\n⚡ Aceleración con caché: {speedup:.2f}x")
        print(f"  - Sin caché: {result1['execution_time_ms']} ms")
        print(f"  - Con caché: {result2['execution_time_ms']} ms")


def test_different_queries() -> None:
    """Prueba el rendimiento con diferentes consultas"""
    print("\n📋 Prueba con diferentes consultas legales")
    
    # Lista de consultas de prueba
    queries = [
        "¿Cuántos días de licencia de maternidad me corresponden?",
        "¿Cuál es el salario mínimo en Colombia?",
        "¿Qué es el fuero de estabilidad laboral reforzada?",
        "¿Cómo se calcula la indemnización por despido sin justa causa?",
        "¿Qué es una justa causa para terminar un contrato laboral?",
        "¿Cuánto tiempo dura el periodo de prueba?",
        "¿Cuáles son los tipos de contrato laboral en Colombia?",
        "¿Qué es una licencia por calamidad doméstica?",
        "¿Qué dice la ley sobre el acoso laboral?",
        "¿Cuáles son los derechos de la mujer embarazada en el trabajo?"
    ]
    
    # Realizar búsquedas
    for query in queries:
        result = test_search(query)
        print_search_result(result)


if __name__ == "__main__":
    print("=" * 80)
    print("✨ Prueba de la funcionalidad de búsqueda BM25 optimizada ✨")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        # Usar la consulta proporcionada como argumento
        query = sys.argv[1]
        print(f"\n📝 Realizando búsqueda con consulta: '{query}'")
        result = test_search(query)
        print_search_result(result)
    else:
        # Ejecutar pruebas completas
        print("\n🧪 Ejecutando pruebas completas:")
        
        # 1. Benchmark de parámetros
        benchmark_parameters()
        
        # 2. Test de sistema de caché
        test_cache_performance()
        
        # 3. Test con diferentes consultas
        test_different_queries()
                
    print("\n✅ Pruebas completadas.") 