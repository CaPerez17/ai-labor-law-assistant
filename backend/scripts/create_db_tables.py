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
        
        # Detectar tipo de base de datos
        db_type = "sqlite" if "sqlite" in database_url else "postgresql"
        print(f"📊 Tipo de base de datos detectada: {db_type}")
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa")
        
        # Limpiar completamente las tablas problemáticas
        print("🗑️ Limpiando tablas existentes...")
        with engine.connect() as conn:
            with conn.begin():  # Manejar transacción explícitamente
                # Eliminar en orden inverso debido a foreign keys
                tables_to_drop = ['mensajes', 'documentos', 'casos', 'usuarios']
                for table in tables_to_drop:
                    if db_type == "sqlite":
                        # SQLite no soporta CASCADE
                        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    else:
                        # PostgreSQL sí soporta CASCADE
                        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            print("✅ Tablas eliminadas")
        
        # Crear tablas con SQL ultra-simple
        print("🏗️ Creando tablas desde cero...")
        return create_tables_simple(engine, db_type)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def create_tables_simple(engine, db_type):
    """Crear tablas con SQL ultra-simple para máxima compatibilidad"""
    from sqlalchemy import text, inspect  # Import aquí también
    
    # SQL compatible con ambos tipos de DB
    if db_type == "sqlite":
        # SQLite usa AUTOINCREMENT en lugar de SERIAL
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
    else:
        # PostgreSQL usa SERIAL
        id_type = "SERIAL PRIMARY KEY"
    
    sql_commands = [
        # 1. Tabla usuarios
        f"""
        CREATE TABLE usuarios (
            id {id_type},
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
        
        # 2. Tabla casos
        f"""
        CREATE TABLE casos (
            id {id_type},
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
        
        # 3. Tabla documentos
        f"""
        CREATE TABLE documentos (
            id {id_type},
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
        
        # 4. Tabla mensajes (CON caso_id)
        f"""
        CREATE TABLE mensajes (
            id {id_type},
            remitente_id INTEGER NOT NULL,
            receptor_id INTEGER NOT NULL,
            caso_id INTEGER,
            contenido VARCHAR(500) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            leido BOOLEAN NOT NULL DEFAULT FALSE
        );
        """,
    ]
    
    # Foreign keys solo para PostgreSQL (SQLite puede tener problemas)
    if db_type == "postgresql":
        foreign_key_commands = [
            # 5. Añadir foreign keys SOLO para casos
            """
            ALTER TABLE casos 
            ADD CONSTRAINT fk_casos_cliente 
            FOREIGN KEY (cliente_id) REFERENCES usuarios(id);
            """,
            
            """
            ALTER TABLE casos 
            ADD CONSTRAINT fk_casos_abogado 
            FOREIGN KEY (abogado_id) REFERENCES usuarios(id);
            """,
            
            # 6. Foreign keys para documentos
            """
            ALTER TABLE documentos 
            ADD CONSTRAINT fk_documentos_usuario 
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
            """,
            
            """
            ALTER TABLE documentos 
            ADD CONSTRAINT fk_documentos_caso 
            FOREIGN KEY (caso_id) REFERENCES casos(id);
            """,
            
            # 7. Foreign keys para mensajes
            """
            ALTER TABLE mensajes 
            ADD CONSTRAINT fk_mensajes_remitente 
            FOREIGN KEY (remitente_id) REFERENCES usuarios(id);
            """,
            
            """
            ALTER TABLE mensajes 
            ADD CONSTRAINT fk_mensajes_receptor 
            FOREIGN KEY (receptor_id) REFERENCES usuarios(id);
            """,
            
            """
            ALTER TABLE mensajes 
            ADD CONSTRAINT fk_mensajes_caso 
            FOREIGN KEY (caso_id) REFERENCES casos(id);
            """,
            
            # 8. Crear índices
            """
            CREATE INDEX idx_casos_cliente_id ON casos(cliente_id);
            """,
            
            """
            CREATE INDEX idx_casos_abogado_id ON casos(abogado_id);
            """
        ]
        sql_commands.extend(foreign_key_commands)
    
    try:
        with engine.connect() as conn:
            with conn.begin():  # Manejar transacción explícitamente
                # Ejecutar cada comando por separado
                for i, sql in enumerate(sql_commands, 1):
                    if db_type == "postgresql":
                        step_names = [
                            "tabla usuarios",
                            "tabla casos", 
                            "tabla documentos",
                            "tabla mensajes",
                            "FK casos->usuarios (cliente)",
                            "FK casos->usuarios (abogado)",
                            "FK documentos->usuarios",
                            "FK documentos->casos",
                            "FK mensajes->usuarios (remitente)",
                            "FK mensajes->usuarios (receptor)",
                            "FK mensajes->casos",
                            "índice casos cliente_id",
                            "índice casos abogado_id"
                        ]
                    else:
                        step_names = [
                            "tabla usuarios",
                            "tabla casos", 
                            "tabla documentos",
                            "tabla mensajes"
                        ]
                    
                    step_name = step_names[i-1] if i <= len(step_names) else f"comando {i}"
                    
                    try:
                        print(f"📋 Ejecutando {i}/{len(sql_commands)}: {step_name}...")
                        conn.execute(text(sql.strip()))
                        print(f"✅ {step_name} completado")
                    except Exception as e:
                        print(f"⚠️ Error en {step_name}: {e}")
                        # Continuar con el siguiente comando
                        continue
                
                print("✅ Proceso de creación de tablas completado")
                
                # Verificación final
                inspector = inspect(engine)
                tables_created = inspector.get_table_names()
                print(f"📋 Tablas creadas: {tables_created}")
                
                if 'casos' in tables_created:
                    casos_columns = [col['name'] for col in inspector.get_columns('casos')]
                    print(f"📋 Columnas en tabla casos: {casos_columns}")
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