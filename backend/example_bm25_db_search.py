#!/usr/bin/env python
"""
Ejemplo de Búsqueda BM25 con Base de Datos
----------------------------------------
Este script muestra cómo utilizar el servicio optimizado BM25 para realizar
búsquedas en documentos legales almacenados en la base de datos.
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("bm25_example")

# Asegurar que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar clases y funciones necesarias
from config import DATABASE_URL
from app.db.database import Base, get_db
from app.models.legal_document import LegalDocument, DocumentType
from app.schemas.legal_document import SearchQuery
from app.services.optimized_bm25_service import OptimizedBM25Service

def format_result(result: Dict[str, Any], show_snippet: bool = True) -> str:
    """Formatea un resultado de búsqueda para su visualización"""
    output = [
        f"ID: {result['document_id']}",
        f"Título: {result['title']}",
        f"Referencia: {result['reference_number']}",
        f"Tipo: {result['document_type']}",
        f"Relevancia: {result['relevance_score']:.3f}"
    ]
    
    if show_snippet:
        output.append(f"Snippet: {result['snippet']}")
    
    return "\n  ".join(output)

def search_documents(query_text: str, 
                     doc_type: str = None, 
                     category: str = None, 
                     limit: int = 5,
                     show_snippets: bool = True,
                     force_reindex: bool = False) -> None:
    """
    Realiza una búsqueda BM25 en los documentos almacenados en la base de datos.
    
    Args:
        query_text: Texto de la consulta
        doc_type: Tipo de documento a filtrar (opcional)
        category: Categoría a filtrar (opcional)
        limit: Número máximo de resultados
        show_snippets: Si se deben mostrar snippets de texto
        force_reindex: Forzar reconstrucción del índice
    """
    # Crear conexión a la base de datos
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Instanciar el servicio optimizado de BM25
        logger.info(f"Inicializando servicio BM25 optimizado...")
        bm25_service = OptimizedBM25Service(
            k1=1.5,  # Parámetro de saturación de términos
            b=0.75,  # Parámetro de normalización de longitud
            use_cache=True,
            force_rebuild=force_reindex
        )
        
        # Verificar documentos en la base de datos
        doc_count = session.query(LegalDocument).count()
        logger.info(f"Documentos en la base de datos: {doc_count}")
        
        if doc_count == 0:
            logger.error("No hay documentos en la base de datos. Carga documentos primero.")
            return
        
        # Convertir el tipo de documento si se especificó
        document_type = None
        if doc_type:
            try:
                document_type = DocumentType(doc_type.lower())
                logger.info(f"Filtrando por tipo de documento: {document_type}")
            except ValueError:
                logger.warning(f"Tipo de documento inválido: {doc_type}")
                valid_types = [t.value for t in DocumentType]
                logger.info(f"Tipos válidos: {', '.join(valid_types)}")
        
        # Crear objeto de consulta
        search_query = SearchQuery(
            query=query_text,
            document_type=document_type,
            category=category,
            limit=limit
        )
        
        # Realizar la búsqueda
        logger.info(f"Ejecutando búsqueda BM25: '{query_text}'")
        start_time = time.time()
        
        # Esta es la línea clave - Búsqueda BM25 desde la base de datos
        results = bm25_service.search_documents(session, search_query)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Búsqueda completada en {elapsed_time:.3f} segundos")
        
        # Mostrar resultados
        if results:
            logger.info(f"Encontrados {len(results)} documentos relevantes:")
            for i, result in enumerate(results, 1):
                print(f"\nResultado {i}:")
                print(f"  {format_result(result, show_snippets)}")
                
            # Mostrar estado del índice
            index_status = bm25_service.index_status()
            logger.info(f"Estado del índice BM25: {index_status['document_count']} documentos indexados")
        else:
            logger.warning("No se encontraron documentos relevantes para la consulta.")
    
    except Exception as e:
        logger.error(f"Error al realizar la búsqueda: {str(e)}")
    finally:
        session.close()

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description='Búsqueda BM25 en documentos legales de la base de datos')
    parser.add_argument('query', help='Texto de la consulta')
    parser.add_argument('--type', '-t', help='Filtrar por tipo de documento')
    parser.add_argument('--category', '-c', help='Filtrar por categoría')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Número máximo de resultados')
    parser.add_argument('--no-snippets', action='store_true', help='No mostrar snippets de texto')
    parser.add_argument('--force-reindex', action='store_true', help='Forzar reconstrucción del índice')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"BÚSQUEDA BM25 EN BASE DE DATOS: '{args.query}'")
    print("=" * 70)
    
    search_documents(
        query_text=args.query,
        doc_type=args.type,
        category=args.category,
        limit=args.limit,
        show_snippets=not args.no_snippets,
        force_reindex=args.force_reindex
    )
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main() 