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

# Configurar logging primero
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

def safe_import():
    """Importar dependencias de manera segura"""
    try:
        from sqlalchemy import create_engine, text, inspect
        from sqlalchemy.orm import sessionmaker
        return True
    except Exception as e:
        logger.error(f"❌ Error importando dependencias: {e}")
        return False

def get_database_url():
    """Obtiene la URL de la base de datos de manera robusta"""
    # Prioridad: variable de entorno -> configuración local
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        try:
            from app.core.config import settings
            database_url = settings.DATABASE_URL
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración: {e}")
            return None
    
    if not database_url:
        logger.error("❌ No se pudo obtener DATABASE_URL")
        return None
        
    logger.info(f"✅ URL de base de datos configurada")
    return database_url

def create_tables_directly(engine):
    """Crear tablas directamente usando SQL para mayor compatibilidad"""
    logger.info("🏗️ Creando tablas usando SQL directo...")
    
    # SQL para crear tabla usuarios
    usuarios_sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        rol VARCHAR(10) NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP,
        activo BOOLEAN DEFAULT TRUE,
        recibir_emails BOOLEAN DEFAULT TRUE,
        fecha_registro TIMESTAMP
    );
    """
    
    # SQL para crear tabla casos
    casos_sql = """
    CREATE TABLE IF NOT EXISTS casos (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(200) NOT NULL,
        descripcion TEXT NOT NULL,
        estado VARCHAR(25) NOT NULL DEFAULT 'PENDIENTE',
        nivel_riesgo VARCHAR(10) NOT NULL DEFAULT 'MEDIO',
        comentarios TEXT,
        cliente_id INTEGER REFERENCES usuarios(id),
        abogado_id INTEGER REFERENCES usuarios(id),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_cierre TIMESTAMP
    );
    """
    
    # SQL para otras tablas importantes
    documentos_sql = """
    CREATE TABLE IF NOT EXISTS documentos (
        id SERIAL PRIMARY KEY,
        nombre_archivo VARCHAR NOT NULL,
        ruta VARCHAR NOT NULL,
        fecha DATE NOT NULL,
        numero_ley VARCHAR NOT NULL,
        categoria VARCHAR NOT NULL,
        subcategoria VARCHAR NOT NULL,
        usuario_id INTEGER REFERENCES usuarios(id),
        caso_id INTEGER REFERENCES casos(id)
    );
    """
    
    try:
        with engine.connect() as conn:
            # Usar transacción para PostgreSQL/SQLite compatibilidad
            trans = conn.begin()
            try:
                # Ajustar SQL para SQLite si es necesario
                if "sqlite" in str(engine.url).lower():
                    usuarios_sql = usuarios_sql.replace("SERIAL", "INTEGER").replace("REFERENCES", "-- REFERENCES")
                    casos_sql = casos_sql.replace("SERIAL", "INTEGER").replace("REFERENCES", "-- REFERENCES")
                    documentos_sql = documentos_sql.replace("SERIAL", "INTEGER").replace("REFERENCES", "-- REFERENCES")
                
                logger.info("📋 Creando tabla usuarios...")
                conn.execute(text(usuarios_sql))
                
                logger.info("📋 Creando tabla casos...")
                conn.execute(text(casos_sql))
                
                logger.info("📋 Creando tabla documentos...")
                conn.execute(text(documentos_sql))
                
                trans.commit()
                logger.info("✅ Tablas creadas exitosamente")
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Error en transacción: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        return False

def create_test_data(engine):
    """Crear datos de prueba básicos"""
    logger.info("👥 Creando datos de prueba...")
    
    # Verificar si ya existen usuarios
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
            user_count = result.scalar()
            
            if user_count > 0:
                logger.info(f"👥 Ya existen {user_count} usuarios")
                return True
            
            # Crear usuarios básicos
            usuarios_data = [
                ("Admin Test", "admin@legalassista.com", "$2b$12$abcdefghijklmnopqrstuvwxyz", "ADMIN"),
                ("Abogado Test", "abogado@legalassista.com", "$2b$12$abcdefghijklmnopqrstuvwxyz", "ABOGADO"),
                ("Cliente Test", "cliente@legalassista.com", "$2b$12$abcdefghijklmnopqrstuvwxyz", "CLIENTE")
            ]
            
            for nombre, email, password_hash, rol in usuarios_data:
                conn.execute(text("""
                    INSERT INTO usuarios (nombre, email, password_hash, rol, activo, recibir_emails, fecha_registro)
                    VALUES (:nombre, :email, :password_hash, :rol, TRUE, TRUE, CURRENT_TIMESTAMP)
                """), {
                    "nombre": nombre,
                    "email": email, 
                    "password_hash": password_hash,
                    "rol": rol
                })
            
            conn.commit()
            logger.info("✅ Usuarios de prueba creados")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creando usuarios de prueba: {e}")
        return False

def main():
    """Función principal para corregir la base de datos"""
    logger.info("🔧 Iniciando corrección de base de datos de producción...")
    
    # Verificar imports
    if not safe_import():
        return False
    
    # Obtener URL de base de datos
    database_url = get_database_url()
    if not database_url:
        return False
    
    try:
        # Importar sqlalchemy después de verificar que está disponible
        from sqlalchemy import create_engine, inspect
        
        # Crear engine
        logger.info("🔗 Conectando a la base de datos...")
        engine = create_engine(database_url)
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Conexión a base de datos exitosa")
        
        # Verificar tablas existentes
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"📋 Tablas existentes: {existing_tables}")
        
        # Crear tablas si no existen
        if 'casos' not in existing_tables or 'usuarios' not in existing_tables:
            if not create_tables_directly(engine):
                return False
        
        # Verificar estructura de tabla casos
        if 'casos' in inspector.get_table_names():
            casos_columns = [col['name'] for col in inspector.get_columns('casos')]
            logger.info(f"📋 Columnas en tabla casos: {casos_columns}")
            
            required_columns = ['comentarios', 'nivel_riesgo']
            missing_columns = [col for col in required_columns if col not in casos_columns]
            
            if missing_columns:
                logger.warning(f"⚠️ Columnas faltantes: {missing_columns}")
                # Intentar añadir columnas faltantes
                try:
                    with engine.connect() as conn:
                        for col in missing_columns:
                            if col == 'comentarios':
                                conn.execute(text("ALTER TABLE casos ADD COLUMN comentarios TEXT"))
                            elif col == 'nivel_riesgo':
                                conn.execute(text("ALTER TABLE casos ADD COLUMN nivel_riesgo VARCHAR(10) DEFAULT 'MEDIO'"))
                        conn.commit()
                        logger.info("✅ Columnas faltantes añadidas")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudieron añadir columnas: {e}")
            else:
                logger.info("✅ Tabla casos tiene todas las columnas necesarias")
        
        # Crear datos de prueba
        create_test_data(engine)
        
        logger.info("✅ Corrección de base de datos completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la corrección de base de datos: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logger.info("🎉 Script completado exitosamente")
        else:
            logger.error("💥 Script falló")
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        sys.exit(1) 