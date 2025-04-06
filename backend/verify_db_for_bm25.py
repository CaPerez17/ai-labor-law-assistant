#!/usr/bin/env python
"""
Verificador de Base de Datos para BM25
------------------------------------
Este script verifica que la estructura de la base de datos sea compatible
con la implementación BM25 y proporciona información sobre el estado de
los documentos almacenados.
"""

import sys
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("bm25_db_verifier")

# Asegurar que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar configuración y modelos
from config import DATABASE_URL
from app.db.database import Base, get_db
from app.models.legal_document import LegalDocument
from app.services.search_service import SearchService, BM25Okapi

def verify_database_structure():
    """Verifica la estructura de la base de datos para compatibilidad con BM25"""
    logger.info("Verificando estructura de la base de datos...")
    
    # Conectar a la base de datos
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # Verificar si la tabla legal_documents existe
    if "legal_documents" not in inspector.get_table_names():
        logger.error("❌ La tabla 'legal_documents' no existe en la base de datos.")
        logger.info("Ejecuta 'python load_documents.py --create-tables' para crear las tablas.")
        return False
    
    # Verificar las columnas necesarias para BM25
    columns = {c["name"] for c in inspector.get_columns("legal_documents")}
    required_columns = {"id", "title", "content", "document_type", "reference_number"}
    
    missing_columns = required_columns - columns
    if missing_columns:
        logger.error(f"❌ Faltan columnas necesarias en la tabla 'legal_documents': {missing_columns}")
        return False
    
    logger.info("✅ Estructura de base de datos es compatible con BM25.")
    return True

def check_document_content():
    """Verifica el contenido de los documentos almacenados"""
    logger.info("Verificando documentos almacenados...")
    
    # Crear sesión
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Contar documentos
    doc_count = session.query(LegalDocument).count()
    logger.info(f"Total de documentos en la base de datos: {doc_count}")
    
    if doc_count == 0:
        logger.warning("⚠️ No hay documentos en la base de datos.")
        logger.info("Ejecuta 'python load_documents.py' para cargar documentos de ejemplo.")
        return False
    
    # Verificar contenido
    empty_content = session.query(LegalDocument).filter(
        (LegalDocument.content.is_(None)) | (LegalDocument.content == "")
    ).count()
    
    if empty_content > 0:
        logger.warning(f"⚠️ {empty_content} documentos tienen contenido vacío.")
    
    # Mostrar muestra de documentos
    sample_docs = session.query(LegalDocument).limit(3).all()
    logger.info("Muestra de documentos:")
    for i, doc in enumerate(sample_docs, 1):
        content_preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
        logger.info(f"Documento {i}: ID={doc.id}, Título='{doc.title}', Tipo='{doc.document_type}'")
        logger.info(f"   Contenido: {content_preview}")
    
    session.close()
    return doc_count > 0

def test_bm25_initialization():
    """Prueba inicializar BM25 con documentos de la base de datos"""
    logger.info("Probando inicialización de BM25 con documentos de la base de datos...")
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Obtener documentos
        documents = session.query(LegalDocument).all()
        
        if not documents:
            logger.warning("⚠️ No se pueden inicializar los índices BM25 sin documentos.")
            return False
        
        # Instanciar servicio de búsqueda
        search_service = SearchService()
        
        # Preprocesar contenido para BM25
        preprocessed_docs = [search_service.preprocess_text(doc.content) for doc in documents]
        
        # Intentar inicializar BM25
        bm25_index = BM25Okapi(preprocessed_docs)
        
        # Verificar que el índice se inicializó correctamente
        if bm25_index:
            logger.info(f"✅ BM25 inicializado correctamente con {len(documents)} documentos.")
            
            # Prueba rápida de búsqueda
            test_query = "vacaciones"
            tokenized_query = search_service.preprocess_text(test_query)
            scores = bm25_index.get_scores(tokenized_query)
            
            # Encontrar documento con mayor puntuación
            max_score_idx = scores.argmax() if len(scores) > 0 else -1
            if max_score_idx >= 0:
                doc = documents[max_score_idx]
                logger.info(f"Prueba de búsqueda con término '{test_query}':")
                logger.info(f"   Documento más relevante: ID={doc.id}, Título='{doc.title}'")
                logger.info(f"   Puntuación: {scores[max_score_idx]}")
            
            return True
        else:
            logger.error("❌ Error al inicializar BM25.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error al inicializar BM25: {str(e)}")
        return False
    finally:
        session.close()

def main():
    """Función principal que ejecuta todas las verificaciones"""
    logger.info("=" * 50)
    logger.info("VERIFICADOR DE COMPATIBILIDAD BM25 CON BASE DE DATOS")
    logger.info("=" * 50)
    logger.info(f"URL de base de datos: {DATABASE_URL}")
    
    structure_ok = verify_database_structure()
    if not structure_ok:
        logger.error("❌ La estructura de la base de datos no es compatible con BM25.")
        return
        
    docs_ok = check_document_content()
    if not docs_ok:
        logger.warning("⚠️ Problemas con los documentos en la base de datos.")
    
    bm25_ok = test_bm25_initialization()
    if not bm25_ok:
        logger.error("❌ No se pudo inicializar BM25 correctamente.")
        return
    
    logger.info("=" * 50)
    if structure_ok and docs_ok and bm25_ok:
        logger.info("✅ RESULTADO: La base de datos es compatible con BM25.")
    else:
        logger.warning("⚠️ RESULTADO: Se encontraron problemas. Revisa los mensajes anteriores.")
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 