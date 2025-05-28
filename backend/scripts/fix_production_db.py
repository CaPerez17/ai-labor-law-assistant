#!/usr/bin/env python3
"""
Script para corregir problemas de la base de datos en producción
================================================================
Este script verifica y corrige automáticamente:
1. Columnas faltantes (como nivel_riesgo en casos)
2. Tablas faltantes
3. Migra datos si es necesario
"""

import os
import sys
import logging
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Obtiene la URL de la base de datos desde variables de entorno o configuración"""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL no encontrada en variables de entorno")
        # Intentar usar configuración local
        database_url = getattr(settings, 'DATABASE_URL', None)
    
    if not database_url:
        logger.error("No se pudo obtener DATABASE_URL")
        return None
        
    logger.info(f"Usando base de datos: {database_url[:50]}...")
    return database_url

def check_table_exists(inspector, table_name):
    """Verifica si una tabla existe"""
    return table_name in inspector.get_table_names()

def check_column_exists(inspector, table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    if not check_table_exists(inspector, table_name):
        return False
    
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def fix_casos_table(engine):
    """Corrige la tabla casos añadiendo la columna nivel_riesgo si no existe"""
    inspector = inspect(engine)
    
    if not check_table_exists(inspector, 'casos'):
        logger.error("❌ Tabla 'casos' no existe. Se requiere ejecutar migraciones completas.")
        return False
    
    if not check_column_exists(inspector, 'casos', 'nivel_riesgo'):
        logger.info("Añadiendo columna 'nivel_riesgo' a la tabla casos...")
        
        with engine.connect() as conn:
            try:
                # Para PostgreSQL
                if "postgresql" in str(engine.url):
                    # Crear enum si no existe
                    conn.execute(text("""
                        DO $$ BEGIN
                            CREATE TYPE nivelriesgo AS ENUM ('BAJO', 'MEDIO', 'ALTO', 'CRITICO');
                        EXCEPTION
                            WHEN duplicate_object THEN null;
                        END $$;
                    """))
                    
                    # Añadir columna
                    conn.execute(text("""
                        ALTER TABLE casos 
                        ADD COLUMN nivel_riesgo nivelriesgo DEFAULT 'MEDIO' NOT NULL;
                    """))
                
                # Para SQLite
                else:
                    conn.execute(text("""
                        ALTER TABLE casos 
                        ADD COLUMN nivel_riesgo TEXT DEFAULT 'MEDIO' NOT NULL;
                    """))
                
                conn.commit()
                logger.info("✅ Columna 'nivel_riesgo' añadida exitosamente")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error al añadir columna nivel_riesgo: {e}")
                conn.rollback()
                return False
    else:
        logger.info("✅ Columna 'nivel_riesgo' ya existe en la tabla casos")
        return True

def verify_critical_tables(engine):
    """Verifica que las tablas críticas existan"""
    inspector = inspect(engine)
    
    critical_tables = ['usuarios', 'casos', 'documentos', 'notificaciones', 'facturas', 'mensajes']
    missing_tables = []
    
    for table in critical_tables:
        if not check_table_exists(inspector, table):
            missing_tables.append(table)
            logger.error(f"❌ Tabla crítica faltante: {table}")
        else:
            logger.info(f"✅ Tabla verificada: {table}")
    
    return len(missing_tables) == 0, missing_tables

def create_essential_tables(engine):
    """Crea tablas esenciales si no existen"""
    try:
        # Importar todos los modelos para asegurar que se registren
        from app.models.usuario import Usuario
        from app.models.caso import Caso
        from app.models.documento import Documento
        from app.models.notificacion import Notificacion
        from app.models.factura import Factura
        from app.models.mensaje import Mensaje
        from app.db.base_class import Base
        
        logger.info("Creando tablas faltantes...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {e}")
        return False

def main():
    """Función principal para corregir la base de datos"""
    logger.info("🔧 Iniciando corrección de base de datos...")
    
    # Obtener URL de base de datos
    database_url = get_database_url()
    if not database_url:
        return False
    
    try:
        # Crear conexión
        engine = create_engine(database_url)
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Conexión a base de datos exitosa")
        
        # Verificar tablas críticas
        tables_ok, missing_tables = verify_critical_tables(engine)
        
        if not tables_ok:
            logger.info(f"Creando {len(missing_tables)} tablas faltantes...")
            if not create_essential_tables(engine):
                return False
        
        # Corregir tabla casos
        if not fix_casos_table(engine):
            logger.warning("⚠️ No se pudo corregir completamente la tabla casos")
        
        logger.info("✅ Corrección de base de datos completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 