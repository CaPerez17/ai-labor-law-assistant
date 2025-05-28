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
    """Método alternativo usando SQL directo optimizado para PostgreSQL"""
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
        
        # Determinar si es PostgreSQL o SQLite
        is_postgres = "postgresql" in database_url
        
        if is_postgres:
            # SQL para PostgreSQL
            sql_commands = [
                # Crear tipos ENUM para PostgreSQL
                """
                DO $$ BEGIN
                    CREATE TYPE rolusuario AS ENUM ('ADMIN', 'ABOGADO', 'CLIENTE');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                """
                DO $$ BEGIN
                    CREATE TYPE estadocaso AS ENUM ('PENDIENTE', 'EN_PROCESO', 'PENDIENTE_VERIFICACION', 'VERIFICADO', 'RESUELTO', 'CERRADO');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                """
                DO $$ BEGIN
                    CREATE TYPE nivelriesgo AS ENUM ('BAJO', 'MEDIO', 'ALTO', 'CRITICO');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                # Tabla usuarios
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    rol rolusuario NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE,
                    recibir_emails BOOLEAN DEFAULT TRUE,
                    fecha_registro TIMESTAMP
                )
                """,
                # Tabla casos
                """
                CREATE TABLE IF NOT EXISTS casos (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    descripcion TEXT NOT NULL,
                    estado estadocaso NOT NULL DEFAULT 'PENDIENTE',
                    nivel_riesgo nivelriesgo NOT NULL DEFAULT 'MEDIO',
                    comentarios TEXT,
                    cliente_id INTEGER NOT NULL REFERENCES usuarios(id),
                    abogado_id INTEGER REFERENCES usuarios(id),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    fecha_cierre TIMESTAMP
                )
                """,
                # Tabla documentos
                """
                CREATE TABLE IF NOT EXISTS documentos (
                    id SERIAL PRIMARY KEY,
                    nombre_archivo VARCHAR NOT NULL,
                    ruta VARCHAR NOT NULL,
                    fecha DATE NOT NULL,
                    numero_ley VARCHAR NOT NULL,
                    categoria VARCHAR NOT NULL,
                    subcategoria VARCHAR NOT NULL,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    caso_id INTEGER REFERENCES casos(id)
                )
                """,
                # Tabla notificaciones
                """
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    tipo VARCHAR(12) NOT NULL,
                    titulo VARCHAR NOT NULL,
                    mensaje VARCHAR NOT NULL,
                    leido BOOLEAN DEFAULT FALSE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_lectura TIMESTAMP,
                    datos_adicionales VARCHAR
                )
                """,
                # Tabla mensajes
                """
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY,
                    remitente_id INTEGER NOT NULL REFERENCES usuarios(id),
                    receptor_id INTEGER NOT NULL REFERENCES usuarios(id),
                    caso_id INTEGER REFERENCES casos(id),
                    contenido VARCHAR(500) NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    leido BOOLEAN NOT NULL DEFAULT FALSE
                )
                """,
                # Tabla facturas
                """
                CREATE TABLE IF NOT EXISTS facturas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    servicio VARCHAR(255) NOT NULL,
                    monto FLOAT NOT NULL,
                    estado VARCHAR(14) NOT NULL,
                    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_pago TIMESTAMP,
                    numero_factura VARCHAR(20) NOT NULL UNIQUE,
                    descripcion VARCHAR(500),
                    metodo_pago VARCHAR(50),
                    mercadopago_id VARCHAR(100),
                    mercadopago_status VARCHAR(50),
                    mercadopago_external_reference VARCHAR(100),
                    mercadopago_payment_id VARCHAR(100)
                )
                """
            ]
        else:
            # SQL para SQLite
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY,
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
                    id INTEGER PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    descripcion TEXT NOT NULL,
                    estado VARCHAR(25) NOT NULL DEFAULT 'PENDIENTE',
                    nivel_riesgo VARCHAR(10) NOT NULL DEFAULT 'MEDIO',
                    comentarios TEXT,
                    cliente_id INTEGER NOT NULL,
                    abogado_id INTEGER,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    fecha_cierre TIMESTAMP
                )
                """
            ]
        
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    table_name = "comando" if is_postgres and i <= 3 else sql.split()[5] if len(sql.split()) > 5 else f"paso-{i}"
                    print(f"📋 Ejecutando {i}/{len(sql_commands)}: {table_name}...")
                    conn.execute(text(sql))
                except Exception as e:
                    print(f"⚠️ Error en comando {i}: {e}")
                    # Continuar con los siguientes comandos
            
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