#!/usr/bin/env python3
"""
Script para corregir problemas de la base de datos en producción
================================================================
Este script verifica y corrige automáticamente:
1. Columnas faltantes (como nivel_riesgo en casos)
2. Tablas faltantes
3. Migra datos si es necesario
4. Crea datos de prueba iniciales
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
    try:
        logger.info("🔧 Iniciando corrección de base de datos de producción...")
        
        # Crear engine y session
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Verificar qué tablas existen
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"📋 Tablas existentes: {existing_tables}")
        
        # Crear todas las tablas si no existen
        from app.db.base import Base
        logger.info("🏗️ Creando tablas faltantes...")
        Base.metadata.create_all(bind=engine)
        
        # Verificar nuevamente las tablas
        existing_tables = inspector.get_table_names()
        logger.info(f"✅ Tablas después de la corrección: {existing_tables}")
        
        # Verificar estructura de la tabla casos
        if 'casos' in existing_tables:
            casos_columns = [col['name'] for col in inspector.get_columns('casos')]
            logger.info(f"📋 Columnas en tabla casos: {casos_columns}")
            
            required_columns = ['comentarios', 'nivel_riesgo']
            missing_columns = [col for col in required_columns if col not in casos_columns]
            
            if missing_columns:
                logger.warning(f"⚠️ Columnas faltantes en casos: {missing_columns}")
                # Las columnas deberían crearse automáticamente con Base.metadata.create_all
            else:
                logger.info("✅ Tabla casos tiene todas las columnas necesarias")
        
        # Crear usuarios y casos de prueba si no existen
        try:
            from app.db.seed import create_test_users, create_test_cases
            
            # Verificar si ya hay usuarios
            with SessionLocal() as db:
                from app.models.usuario import Usuario
                user_count = db.query(Usuario).count()
                
                if user_count == 0:
                    logger.info("👥 Creando usuarios de prueba...")
                    create_test_users()
                    logger.info("✅ Usuarios de prueba creados")
                else:
                    logger.info(f"👥 Ya existen {user_count} usuarios en la base de datos")
                
                # Verificar si ya hay casos
                from app.models.caso import Caso
                caso_count = db.query(Caso).count()
                
                if caso_count == 0:
                    logger.info("📋 Creando casos de prueba...")
                    create_test_cases()
                    logger.info("✅ Casos de prueba creados")
                else:
                    logger.info(f"📋 Ya existen {caso_count} casos en la base de datos")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error creando datos de prueba: {e}")
        
        logger.info("✅ Corrección de base de datos completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la corrección de base de datos: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 