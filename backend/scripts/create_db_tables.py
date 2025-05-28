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

def main():
    print("🔧 Iniciando creación de tablas de base de datos...")
    
    # Obtener URL de base de datos
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        try:
            from app.core.config import settings
            database_url = settings.DATABASE_URL
        except Exception as e:
            print(f"❌ Error obteniendo configuración: {e}")
            return False
    
    print(f"🔗 Conectando a base de datos PostgreSQL...")
    
    try:
        from sqlalchemy import create_engine, text, inspect
        engine = create_engine(database_url)
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a PostgreSQL")
        
        # Verificar qué tablas existen actualmente
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"📋 Tablas existentes: {existing_tables}")
        
        # Si la tabla casos existe pero no tiene cliente_id, la recreamos
        if 'casos' in existing_tables:
            casos_columns = [col['name'] for col in inspector.get_columns('casos')]
            print(f"📋 Columnas en tabla casos: {casos_columns}")
            
            if 'cliente_id' not in casos_columns:
                print("⚠️ Tabla casos no tiene cliente_id, eliminando y recreando...")
                with engine.connect() as conn:
                    conn.execute(text("DROP TABLE IF EXISTS casos CASCADE"))
                    conn.commit()
                    print("🗑️ Tabla casos eliminada")
        
        # Crear tablas con SQL directo y optimizado
        print("🏗️ Creando todas las tablas con SQL directo...")
        return create_tables_postgresql(engine)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def create_tables_postgresql(engine):
    """Crear tablas específicamente para PostgreSQL"""
    from sqlalchemy import text
    
    sql_commands = [
        # 1. Crear tipos ENUM
        """
        DO $$ BEGIN
            CREATE TYPE rolusuario AS ENUM ('ADMIN', 'ABOGADO', 'CLIENTE');
        EXCEPTION
            WHEN duplicate_object THEN 
                RAISE NOTICE 'Tipo rolusuario ya existe';
        END $$;
        """,
        """
        DO $$ BEGIN
            CREATE TYPE estadocaso AS ENUM ('PENDIENTE', 'EN_PROCESO', 'PENDIENTE_VERIFICACION', 'VERIFICADO', 'RESUELTO', 'CERRADO');
        EXCEPTION
            WHEN duplicate_object THEN 
                RAISE NOTICE 'Tipo estadocaso ya existe';
        END $$;
        """,
        """
        DO $$ BEGIN
            CREATE TYPE nivelriesgo AS ENUM ('BAJO', 'MEDIO', 'ALTO', 'CRITICO');
        EXCEPTION
            WHEN duplicate_object THEN 
                RAISE NOTICE 'Tipo nivelriesgo ya existe';
        END $$;
        """,
        
        # 2. Crear tabla usuarios
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
        );
        """,
        
        # 3. Crear tabla casos CON foreign keys explícitas
        """
        CREATE TABLE IF NOT EXISTS casos (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            descripcion TEXT NOT NULL,
            estado estadocaso NOT NULL DEFAULT 'PENDIENTE',
            nivel_riesgo nivelriesgo NOT NULL DEFAULT 'MEDIO',
            comentarios TEXT,
            cliente_id INTEGER NOT NULL,
            abogado_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            fecha_cierre TIMESTAMP,
            CONSTRAINT fk_casos_cliente FOREIGN KEY (cliente_id) REFERENCES usuarios(id),
            CONSTRAINT fk_casos_abogado FOREIGN KEY (abogado_id) REFERENCES usuarios(id)
        );
        """,
        
        # 4. Crear índices para optimización
        """
        CREATE INDEX IF NOT EXISTS idx_casos_cliente_id ON casos(cliente_id);
        CREATE INDEX IF NOT EXISTS idx_casos_abogado_id ON casos(abogado_id);
        CREATE INDEX IF NOT EXISTS idx_casos_estado ON casos(estado);
        """,
        
        # 5. Otras tablas importantes
        """
        CREATE TABLE IF NOT EXISTS documentos (
            id SERIAL PRIMARY KEY,
            nombre_archivo VARCHAR NOT NULL,
            ruta VARCHAR NOT NULL,
            fecha DATE NOT NULL,
            numero_ley VARCHAR NOT NULL,
            categoria VARCHAR NOT NULL,
            subcategoria VARCHAR NOT NULL,
            usuario_id INTEGER NOT NULL,
            caso_id INTEGER,
            CONSTRAINT fk_documentos_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            CONSTRAINT fk_documentos_caso FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        """,
        
        """
        CREATE TABLE IF NOT EXISTS mensajes (
            id SERIAL PRIMARY KEY,
            remitente_id INTEGER NOT NULL,
            receptor_id INTEGER NOT NULL,
            caso_id INTEGER,
            contenido VARCHAR(500) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            leido BOOLEAN NOT NULL DEFAULT FALSE,
            CONSTRAINT fk_mensajes_remitente FOREIGN KEY (remitente_id) REFERENCES usuarios(id),
            CONSTRAINT fk_mensajes_receptor FOREIGN KEY (receptor_id) REFERENCES usuarios(id),
            CONSTRAINT fk_mensajes_caso FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        """
    ]
    
    try:
        with engine.connect() as conn:
            # Usar una sola transacción para todo
            trans = conn.begin()
            
            try:
                for i, sql in enumerate(sql_commands, 1):
                    step_name = [
                        "tipos ENUM rolusuario",
                        "tipos ENUM estadocaso", 
                        "tipos ENUM nivelriesgo",
                        "tabla usuarios",
                        "tabla casos",
                        "índices casos",
                        "tabla documentos",
                        "tabla mensajes"
                    ][i-1] if i <= 8 else f"comando {i}"
                    
                    print(f"📋 Ejecutando {i}/{len(sql_commands)}: {step_name}...")
                    conn.execute(text(sql))
                
                trans.commit()
                print("✅ Todas las tablas creadas exitosamente")
                
                # Verificar que la tabla casos tiene cliente_id
                inspector = inspect(engine)
                if 'casos' in inspector.get_table_names():
                    casos_columns = [col['name'] for col in inspector.get_columns('casos')]
                    if 'cliente_id' in casos_columns:
                        print("✅ Verificado: tabla casos tiene columna cliente_id")
                    else:
                        print("❌ ERROR: tabla casos NO tiene columna cliente_id")
                        return False
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error en transacción: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 