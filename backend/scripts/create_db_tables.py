#!/usr/bin/env python3
"""
Script simple para crear tablas de base de datos
===============================================
Crea todas las tablas necesarias usando SQL directo compatible
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
    
    print(f"🔗 Conectando a base de datos...")
    
    try:
        from sqlalchemy import create_engine, text, inspect
        engine = create_engine(database_url)
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa")
        
        # Verificar y recrear tabla casos si es necesario
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"📋 Tablas existentes: {existing_tables}")
        
        # Limpiar y recrear tablas problemáticas
        if 'casos' in existing_tables:
            print("🗑️ Eliminando tabla casos para recrear...")
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS casos CASCADE"))
                conn.commit()
        
        # Crear tablas con SQL simple y compatible
        print("🏗️ Creando tablas con SQL compatible...")
        return create_tables_simple(engine)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def create_tables_simple(engine):
    """Crear tablas con SQL simple sin ENUM para máxima compatibilidad"""
    from sqlalchemy import text
    
    sql_commands = [
        # 1. Tabla usuarios - simple y directo
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE,
            recibir_emails BOOLEAN DEFAULT TRUE,
            fecha_registro TIMESTAMP
        );
        """,
        
        # 2. Tabla casos - con VARCHAR para evitar problemas de ENUM
        """
        CREATE TABLE IF NOT EXISTS casos (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            descripcion TEXT NOT NULL,
            estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
            nivel_riesgo VARCHAR(20) NOT NULL DEFAULT 'MEDIO',
            comentarios TEXT,
            cliente_id INTEGER NOT NULL,
            abogado_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_cierre TIMESTAMP
        );
        """,
        
        # 3. Añadir foreign keys como paso separado
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_casos_cliente'
            ) THEN
                ALTER TABLE casos ADD CONSTRAINT fk_casos_cliente 
                FOREIGN KEY (cliente_id) REFERENCES usuarios(id);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_casos_abogado'
            ) THEN
                ALTER TABLE casos ADD CONSTRAINT fk_casos_abogado 
                FOREIGN KEY (abogado_id) REFERENCES usuarios(id);
            END IF;
        END $$;
        """,
        
        # 4. Crear índices para performance
        """
        CREATE INDEX IF NOT EXISTS idx_casos_cliente_id ON casos(cliente_id);
        CREATE INDEX IF NOT EXISTS idx_casos_abogado_id ON casos(abogado_id);
        CREATE INDEX IF NOT EXISTS idx_casos_estado ON casos(estado);
        """,
        
        # 5. Tabla documentos
        """
        CREATE TABLE IF NOT EXISTS documentos (
            id SERIAL PRIMARY KEY,
            nombre_archivo VARCHAR(255) NOT NULL,
            ruta VARCHAR(500) NOT NULL,
            fecha DATE NOT NULL,
            numero_ley VARCHAR(100) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            subcategoria VARCHAR(100) NOT NULL,
            usuario_id INTEGER NOT NULL,
            caso_id INTEGER
        );
        """,
        
        # 6. Foreign keys para documentos
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_documentos_usuario'
            ) THEN
                ALTER TABLE documentos ADD CONSTRAINT fk_documentos_usuario 
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_documentos_caso'
            ) THEN
                ALTER TABLE documentos ADD CONSTRAINT fk_documentos_caso 
                FOREIGN KEY (caso_id) REFERENCES casos(id);
            END IF;
        END $$;
        """,
        
        # 7. Tabla mensajes
        """
        CREATE TABLE IF NOT EXISTS mensajes (
            id SERIAL PRIMARY KEY,
            remitente_id INTEGER NOT NULL,
            receptor_id INTEGER NOT NULL,
            caso_id INTEGER,
            contenido VARCHAR(500) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            leido BOOLEAN NOT NULL DEFAULT FALSE
        );
        """,
        
        # 8. Foreign keys para mensajes
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_mensajes_remitente'
            ) THEN
                ALTER TABLE mensajes ADD CONSTRAINT fk_mensajes_remitente 
                FOREIGN KEY (remitente_id) REFERENCES usuarios(id);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_mensajes_receptor'
            ) THEN
                ALTER TABLE mensajes ADD CONSTRAINT fk_mensajes_receptor 
                FOREIGN KEY (receptor_id) REFERENCES usuarios(id);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_mensajes_caso'
            ) THEN
                ALTER TABLE mensajes ADD CONSTRAINT fk_mensajes_caso 
                FOREIGN KEY (caso_id) REFERENCES casos(id);
            END IF;
        END $$;
        """
    ]
    
    try:
        with engine.connect() as conn:
            # Ejecutar cada comando por separado para mejor debugging
            for i, sql in enumerate(sql_commands, 1):
                step_name = [
                    "tabla usuarios",
                    "tabla casos", 
                    "foreign keys casos",
                    "índices casos",
                    "tabla documentos",
                    "foreign keys documentos",
                    "tabla mensajes",
                    "foreign keys mensajes"
                ][i-1] if i <= 8 else f"comando {i}"
                
                try:
                    print(f"📋 Ejecutando {i}/{len(sql_commands)}: {step_name}...")
                    conn.execute(text(sql))
                    conn.commit()  # Commit después de cada comando
                    print(f"✅ {step_name} completado")
                except Exception as e:
                    print(f"⚠️ Error en {step_name}: {e}")
                    # Continuar con el siguiente comando
                    continue
            
            print("✅ Proceso de creación de tablas completado")
            
            # Verificación final
            inspector = inspect(engine)
            if 'casos' in inspector.get_table_names():
                casos_columns = [col['name'] for col in inspector.get_columns('casos')]
                if 'cliente_id' in casos_columns:
                    print("✅ VERIFICADO: tabla casos tiene columna cliente_id")
                    return True
                else:
                    print("❌ ERROR: tabla casos NO tiene columna cliente_id")
                    return False
            else:
                print("❌ ERROR: tabla casos no fue creada")
                return False
                
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 