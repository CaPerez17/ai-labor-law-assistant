"""
Script para cargar documentos legales en la base de datos
---------------------------------------------------
Este script procesa documentos legales (PDF, TXT) y los carga en la base de datos.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Asegurarnos de que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar módulos de la aplicación
from app.db.database import SessionLocal, engine, Base
from app.models.legal_document import LegalDocument, DocumentType
from utils.document_processor import DocumentProcessor

def convert_document_type(doc_type: str) -> DocumentType:
    """Convierte el tipo de documento detectado al enum DocumentType"""
    doc_type = doc_type.lower()
    
    # Mapeo de tipos de documentos detectados a valores del enum
    type_mapping = {
        "ley": DocumentType.LEY,
        "decreto": DocumentType.DECRETO,
        "sentencia": DocumentType.SENTENCIA,
        "resolución": DocumentType.RESOLUCION,
        "circular": DocumentType.CIRCULAR,
        "concepto": DocumentType.CONCEPTO,
        "otro": DocumentType.OTRO
    }
    
    # Devolver el tipo correspondiente o el valor por defecto
    return type_mapping.get(doc_type, DocumentType.OTRO)

def save_to_database(documents: List[Dict[str, Any]]) -> int:
    """Guarda los documentos procesados en la base de datos"""
    # Crear una sesión
    db = SessionLocal()
    count = 0
    
    try:
        for doc_data in documents:
            # Convertir el tipo de documento al enum correspondiente
            doc_type = convert_document_type(doc_data["document_type"])
            
            # Crear instancia del modelo
            document = LegalDocument(
                title=doc_data["title"],
                document_type=doc_type,
                reference_number=doc_data["reference_number"],
                issue_date=doc_data["issue_date"] or datetime.now(),  # Usar fecha actual si no se detectó
                source=doc_data["source"],
                content=doc_data["content"],
                keywords=doc_data["keywords"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"]
            )
            
            # Agregar a la sesión
            db.add(document)
            count += 1
            
        # Guardar cambios
        db.commit()
        return count
        
    except Exception as e:
        db.rollback()
        print(f"Error al guardar documentos en la base de datos: {e}")
        return 0
    finally:
        db.close()

def main():
    """Función principal para procesamiento de documentos"""
    parser = argparse.ArgumentParser(description="Procesa documentos legales y los carga en la base de datos")
    parser.add_argument("--dir", type=str, default="data/docs", 
                      help="Directorio con los documentos a procesar")
    parser.add_argument("--pdf-only", action="store_true", 
                       help="Procesar solo archivos PDF")
    parser.add_argument("--txt-only", action="store_true", 
                       help="Procesar solo archivos TXT")
    parser.add_argument("--create-tables", action="store_true", 
                       help="Crear tablas en la base de datos si no existen")
    
    args = parser.parse_args()
    
    # Asegurarnos de que el directorio de datos existe
    data_dir = os.path.join(backend_dir, args.dir)
    if not os.path.exists(data_dir):
        print(f"El directorio {data_dir} no existe. Creando...")
        os.makedirs(data_dir, exist_ok=True)
        
        # Crear subdirectorios para PDF y TXT
        os.makedirs(os.path.join(data_dir, "pdf"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "txt"), exist_ok=True)
        
        print(f"Subdirectorios creados. Por favor, coloque documentos en {data_dir}/pdf o {data_dir}/txt")
        return
    
    # Crear tablas si se solicita
    if args.create_tables:
        print("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
    
    # Instanciar el procesador
    processor = DocumentProcessor()
    
    # Determinar qué directorios procesar
    dirs_to_process = []
    if args.pdf_only:
        pdf_dir = os.path.join(data_dir, "pdf")
        if os.path.exists(pdf_dir):
            dirs_to_process.append(pdf_dir)
    elif args.txt_only:
        txt_dir = os.path.join(data_dir, "txt")
        if os.path.exists(txt_dir):
            dirs_to_process.append(txt_dir)
    else:
        # Procesar todos los directorios
        dirs_to_process.append(data_dir)
    
    # Procesar documentos
    total_docs = 0
    for directory in dirs_to_process:
        print(f"Procesando documentos en {directory}...")
        documents = processor.process_directory(directory)
        
        if documents:
            count = save_to_database(documents)
            print(f"Se han cargado {count} documentos desde {directory} a la base de datos.")
            total_docs += count
        else:
            print(f"No se encontraron documentos para procesar en {directory}.")
    
    print(f"Proceso completado. Total de documentos cargados: {total_docs}")

if __name__ == "__main__":
    main() 