#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el servicio BM25 optimizado con los documentos importados.
Este script prueba el servicio directamente, sin pasar por la API.
"""

import sys
import logging
import argparse
from pathlib import Path

# Ajustar path para importar desde el backend
sys.path.append(str(Path("backend").absolute()))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from app.services.optimized_bm25_service import OptimizedBM25Service
    from app.db.session import engine
except ImportError as e:
    logger.error(f"Error al importar módulos del backend: {str(e)}")
    logger.error("Asegúrate de que el proyecto esté correctamente configurado y que estés ejecutando este script desde la raíz del proyecto.")
    sys.exit(1)

def parse_args():
    """Procesa los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Herramienta de búsqueda BM25 sobre documentos legales")
    parser.add_argument("query", type=str, help="Consulta para buscar en los documentos")
    parser.add_argument("--limit", type=int, default=5, help="Número máximo de resultados a mostrar (default: 5)")
    parser.add_argument("--type", type=str, help="Filtrar por tipo de documento (ej: ley, sentencia)")
    parser.add_argument("--force-reindex", action="store_true", help="Forzar la reconstrucción del índice")
    return parser.parse_args()

def main():
    """Función principal para ejecutar la búsqueda"""
    args = parse_args()
    
    # Inicializar el servicio BM25
    try:
        logger.info("Inicializando servicio BM25 optimizado...")
        service = OptimizedBM25Service(
            db_url=str(engine.url),
            force_rebuild=args.force_reindex
        )
        
        # Verificar si se construyó el índice correctamente
        if not service.is_initialized:
            logger.error("No se pudo inicializar el servicio BM25. Verifique los logs para más detalles.")
            return
            
        # Mostrar estadísticas del índice
        doc_count = service.get_document_count()
        logger.info(f"Índice BM25 inicializado con {doc_count} documentos.")
        
        # Realizar búsqueda
        logger.info(f"Buscando: '{args.query}'")
        start_time = service.get_current_time()
        
        results = service.search(
            query=args.query,
            limit=args.limit,
            filters={"document_type": args.type} if args.type else None
        )
        
        end_time = service.get_current_time()
        search_time = (end_time - start_time).total_seconds()
        
        # Mostrar resultados
        logger.info(f"Búsqueda completada en {search_time:.2f} segundos. {len(results)} resultados encontrados.")
        
        if not results:
            logger.info("No se encontraron documentos que coincidan con la consulta.")
            return
            
        print("\n" + "="*80)
        print(f"RESULTADOS PARA: '{args.query}'")
        print("="*80)
        
        for idx, result in enumerate(results, 1):
            print(f"\n[{idx}] {result['title']}")
            print(f"    ID: {result['id']}")
            print(f"    Tipo: {result['document_type']} - Referencia: {result['reference_number'] or 'N/A'}")
            print(f"    Relevancia: {result['score']:.3f}")
            print(f"    Fragmento: {result['snippet'][:200]}...")
            
        print("\n" + "="*80)
            
    except Exception as e:
        logger.error(f"Error al ejecutar la búsqueda: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 