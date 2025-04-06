#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar documentos legales desde archivos JSON a la base de datos SQLite.

Este script toma los archivos JSON en ./Docs/BaseDeDatos/json_output/ y los importa
a la base de datos SQLite del sistema AI Labor Law Assistant.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constantes
JSON_DIR = "./Docs/BaseDeDatos/json_output"
DB_PATH = "./sql_app.db"  # Ruta a la base de datos SQLite

def connect_db():
    """Conecta a la base de datos SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar a la base de datos: {str(e)}")
        return None

def create_tables_if_not_exist(conn):
    """Crea las tablas necesarias si no existen"""
    try:
        cursor = conn.cursor()
        
        # Crear tabla para documentos legales
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS legal_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            document_subtype TEXT,
            reference_number TEXT,
            source TEXT,
            date TEXT,
            keywords TEXT,
            summary TEXT,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logger.info("Tablas creadas/verificadas con éxito")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al crear tablas: {str(e)}")
        return False

def get_imported_documents(conn):
    """Obtiene los títulos de documentos ya importados para evitar duplicados"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT title, reference_number FROM legal_documents")
        
        imported_docs = {}
        for row in cursor.fetchall():
            key = f"{row['title']}|{row['reference_number']}"
            imported_docs[key] = True
        
        return imported_docs
    except sqlite3.Error as e:
        logger.error(f"Error al obtener documentos importados: {str(e)}")
        return {}

def import_document(conn, json_data, file_path):
    """Importa un documento a la base de datos"""
    try:
        cursor = conn.cursor()
        
        # Preparar datos para inserción
        title = json_data.get("titulo", "")
        document_type = json_data.get("categoria", "")
        document_subtype = json_data.get("subcategoria", "")
        reference_number = json_data.get("numero", "")
        source = json_data.get("fuente", "")
        date = json_data.get("fecha", "")
        
        # Convertir keywords a string JSON
        keywords = json.dumps(json_data.get("palabras_clave", []), ensure_ascii=False)
        
        summary = json_data.get("resumen", "")
        content = json_data.get("texto_completo", "")
        timestamp = datetime.now().isoformat()
        
        # Insertar en la base de datos
        cursor.execute('''
        INSERT INTO legal_documents 
        (title, document_type, document_subtype, reference_number, source, date, 
         keywords, summary, content, created_at, updated_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, document_type, document_subtype, reference_number, source, date, 
              keywords, summary, content, timestamp, timestamp))
        
        conn.commit()
        logger.info(f"Documento importado con éxito: {os.path.basename(file_path)}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al importar documento {file_path}: {str(e)}")
        return False

def main():
    """Función principal para importar documentos"""
    # Conectar a la base de datos
    conn = connect_db()
    if not conn:
        logger.error("No se pudo conectar a la base de datos. Saliendo.")
        return
    
    # Crear tablas si no existen
    if not create_tables_if_not_exist(conn):
        logger.error("No se pudieron crear las tablas necesarias. Saliendo.")
        conn.close()
        return
    
    # Obtener documentos ya importados para evitar duplicados
    imported_docs = get_imported_documents(conn)
    logger.info(f"Se encontraron {len(imported_docs)} documentos ya importados en la base de datos")
    
    # Contador de estadísticas
    total_files = 0
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    # Procesar cada archivo JSON
    for file_name in os.listdir(JSON_DIR):
        if not file_name.endswith('.json'):
            continue
        
        total_files += 1
        file_path = os.path.join(JSON_DIR, file_name)
        
        try:
            # Leer archivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Verificar si el documento es pertinente
            if not json_data.get("pertinente", False):
                logger.warning(f"Documento no pertinente, se omite: {file_name}")
                skipped_count += 1
                continue
            
            # Verificar si el documento ya existe en la base de datos
            doc_key = f"{json_data.get('titulo', '')}|{json_data.get('numero', '')}"
            if doc_key in imported_docs:
                logger.info(f"Documento ya existe en la base de datos, se omite: {file_name}")
                skipped_count += 1
                continue
            
            # Importar documento
            if import_document(conn, json_data, file_path):
                imported_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            logger.error(f"Error procesando {file_name}: {str(e)}")
            error_count += 1
    
    # Cerrar conexión a la base de datos
    conn.close()
    
    # Resumen final
    logger.info(f"\n{'='*50}")
    logger.info(f"RESUMEN DE IMPORTACIÓN")
    logger.info(f"{'='*50}")
    logger.info(f"Total de archivos JSON encontrados: {total_files}")
    logger.info(f"Documentos importados exitosamente: {imported_count}")
    logger.info(f"Documentos omitidos (duplicados o no pertinentes): {skipped_count}")
    logger.info(f"Errores de importación: {error_count}")
    logger.info(f"{'='*50}")

if __name__ == "__main__":
    logger.info("Iniciando importación de documentos legales a la base de datos")
    main()
    logger.info("Importación completada") 