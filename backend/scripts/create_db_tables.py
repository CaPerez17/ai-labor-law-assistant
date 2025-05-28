#!/usr/bin/env python3
"""
Script simple para crear tablas de base de datos
===============================================
Crea todas las tablas necesarias usando SQLAlchemy ORM
"""

import os
import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

def create_tables_with_orm():
    """Método principal usando SQLAlchemy ORM"""
    try:
        print("🔗 Importando dependencias...")
        from sqlalchemy import create_engine
        from app.core.config import settings
        from app.db.base import Base
        
        print("🔗 Conectando a la base de datos...")
        engine = create_engine(settings.DATABASE_URL)
        
        print("🏗️ Creando tablas usando ORM...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Todas las tablas han sido creadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en método ORM: {e}")
        return False

def create_tables_with_sql():
    """Método alternativo usando SQL directo"""
    try:
        print("🔄 Intentando método alternativo con SQL directo...")
        from sqlalchemy import create_engine, text
        
        # Obtener URL de base de datos
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            try:
                from app.core.config import settings
                database_url = settings.DATABASE_URL
            except:
                print("❌ No se pudo obtener DATABASE_URL")
                return False
        
        engine = create_engine(database_url)
        
        # SQL básico para crear tablas principales
        sql_commands = [
            """
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
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS casos (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT NOT NULL,
                estado VARCHAR(25) NOT NULL DEFAULT 'PENDIENTE',
                nivel_riesgo VARCHAR(10) NOT NULL DEFAULT 'MEDIO',
                comentarios TEXT,
                cliente_id INTEGER,
                abogado_id INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_cierre TIMESTAMP
            )
            """
        ]
        
        with engine.connect() as conn:
            # Ajustar para SQLite si es necesario
            if "sqlite" in str(engine.url).lower():
                sql_commands = [cmd.replace("SERIAL", "INTEGER") for cmd in sql_commands]
            
            for sql in sql_commands:
                print(f"📋 Ejecutando: {sql.split()[2]} {sql.split()[5]}...")
                conn.execute(text(sql))
            
            conn.commit()
            print("✅ Tablas creadas con SQL directo")
            return True
        
    except Exception as e:
        print(f"❌ Error en método SQL: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def main():
    print("🔧 Creando tablas de base de datos...")
    
    # Intentar método ORM primero
    if create_tables_with_orm():
        return True
    
    # Si falla, intentar método SQL
    print("⚠️ Método ORM falló, intentando método alternativo...")
    if create_tables_with_sql():
        return True
    
    print("❌ Ambos métodos fallaron")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 