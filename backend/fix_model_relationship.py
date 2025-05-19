"""
Script para reparar la relación entre usuarios y documentos en la base de datos de producción.
Este script modifica la estructura de la tabla usuarios para añadir la relación con documentos.
"""

import os
import sys
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurarnos de que el directorio backend esté en sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importar SQLAlchemy y otros módulos necesarios
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import text

# Obtener DATABASE_URL de las variables de entorno o usar un valor predeterminado
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/legalassista")

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

# Función para verificar si la relación ya existe
def check_relationship_exists():
    try:
        inspector = inspect(engine)
        # Verificar si la tabla documentos existe
        if 'documentos' not in inspector.get_table_names():
            logger.error("La tabla documentos no existe")
            return False
        
        # Verificar si la columna usuario_id existe en documentos
        columns = [c['name'] for c in inspector.get_columns('documentos')]
        if 'usuario_id' not in columns:
            logger.error("La columna usuario_id no existe en la tabla documentos")
            return False
        
        # Verificar si hay alguna constraint de foreign key
        for fk in inspector.get_foreign_keys('documentos'):
            if fk.get('referred_table') == 'usuarios' and 'usuario_id' in fk.get('constrained_columns', []):
                logger.info("La relación entre usuarios y documentos ya existe")
                return True
        
        logger.error("No existe una foreign key entre documentos y usuarios")
        return False
    except Exception as e:
        logger.error(f"Error al verificar la relación: {e}")
        return False

# Función para añadir la relación si no existe
def add_relationship():
    try:
        # Verificar primero si la relación ya existe
        if check_relationship_exists():
            logger.info("La relación ya existe, no es necesario hacer cambios")
            return
        
        # Si no existe, crear la foreign key
        with engine.connect() as conn:
            # Verificar si la tabla documentos existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'documentos')"))
            if not result.scalar():
                logger.error("La tabla documentos no existe")
                return
            
            # Verificar si la tabla usuarios existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'usuarios')"))
            if not result.scalar():
                logger.error("La tabla usuarios no existe")
                return
            
            # Verificar si la columna usuario_id existe en documentos
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'documentos' AND column_name = 'usuario_id')"))
            if not result.scalar():
                logger.info("Añadiendo columna usuario_id a la tabla documentos")
                conn.execute(text("ALTER TABLE documentos ADD COLUMN usuario_id INTEGER"))
            
            # Verificar si la foreign key ya existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.table_constraints tc
                    JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = 'documentos' 
                    AND ccu.table_name = 'usuarios'
                )
            """))
            
            if not result.scalar():
                logger.info("Creando constraint de foreign key entre documentos y usuarios")
                conn.execute(text("""
                    ALTER TABLE documentos 
                    ADD CONSTRAINT fk_documentos_usuarios 
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                """))
                logger.info("Foreign key creada exitosamente")
            else:
                logger.info("La foreign key ya existe")
            
            conn.commit()
        
        logger.info("Relación entre usuarios y documentos añadida exitosamente")
    except Exception as e:
        logger.error(f"Error al añadir la relación: {e}")

# Ejecutar la función principal
if __name__ == "__main__":
    logger.info("Iniciando script para reparar la relación entre usuarios y documentos")
    add_relationship()
    logger.info("Script finalizado") 