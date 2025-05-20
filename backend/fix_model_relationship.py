"""
Script para reparar la relación entre usuarios y documentos en la base de datos de producción.
Este script modifica la estructura de la tabla usuarios para añadir la relación con documentos.
"""

import os
import sys
from pathlib import Path
import logging
import argparse

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

def parse_arguments():
    parser = argparse.ArgumentParser(description='Reparar la relación entre usuarios y documentos en la base de datos')
    parser.add_argument('--postgres', type=str, help='URL de conexión PostgreSQL')
    return parser.parse_args()

def get_database_url():
    # Primero intentar obtener de los argumentos
    args = parse_arguments()
    if args.postgres:
        logger.info(f"Usando URL de conexión proporcionada por parámetro")
        return args.postgres
    
    # Luego intentar obtener de las variables de entorno
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        logger.info(f"Usando URL de conexión de variables de entorno: {db_url}")
        return db_url
    
    # Si no está disponible, preguntar al usuario
    print("Por favor, ingresa la URL de conexión PostgreSQL (ejemplo: postgresql://usuario:password@host:5432/dbname):")
    db_url = input("> ")
    if db_url:
        logger.info(f"Usando URL de conexión ingresada por el usuario")
        return db_url
    
    # Valor predeterminado para desarrollo local
    logger.warning("No se proporcionó URL de conexión, usando valores predeterminados para desarrollo local")
    return "sqlite:///./sql_app.db"

# Función para verificar si la relación ya existe
def check_relationship_exists(engine):
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
def add_relationship(engine):
    try:
        # Verificar primero si la relación ya existe
        if check_relationship_exists(engine):
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
    
    # Obtener la URL de la base de datos
    DATABASE_URL = get_database_url()
    
    try:
        # Crear el motor de la base de datos
        logger.info(f"Conectando a la base de datos: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        
        # Verificar conexión
        with engine.connect() as conn:
            logger.info("Conexión a la base de datos establecida correctamente")
            
            # Listar tablas disponibles
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result]
            logger.info(f"Tablas disponibles en la base de datos: {tables}")
            
            # Añadir la relación
            add_relationship(engine)
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        
    logger.info("Script finalizado") 