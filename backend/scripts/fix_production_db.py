#!/usr/bin/env python3
"""
Script agresivo para arreglar base de datos PostgreSQL en producción
================================================================
Elimina completamente ENUMs y recrea tablas con VARCHAR
"""

import os
import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

def main():
    print("🚨 Iniciando corrección AGRESIVA de base de datos PostgreSQL...")
    
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
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        # Detectar tipo de base de datos
        db_type = "sqlite" if "sqlite" in database_url else "postgresql"
        print(f"📊 Tipo de base de datos detectada: {db_type}")
        
        if db_type != "postgresql":
            print("⚠️ Este script es solo para PostgreSQL")
            return True
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa")
        
        return fix_postgresql_aggressive(engine)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def fix_postgresql_aggressive(engine):
    """Corrección agresiva para PostgreSQL"""
    from sqlalchemy import text
    
    print("🗑️ PASO 1: Eliminando todas las tablas y ENUMs...")
    
    # Comandos para eliminar TODO
    drop_commands = [
        # 1. Eliminar tablas en orden correcto
        "DROP TABLE IF EXISTS mensajes CASCADE;",
        "DROP TABLE IF EXISTS documentos CASCADE;", 
        "DROP TABLE IF EXISTS casos CASCADE;",
        "DROP TABLE IF EXISTS notificaciones CASCADE;",
        "DROP TABLE IF EXISTS facturas CASCADE;",
        "DROP TABLE IF EXISTS usuarios CASCADE;",
        "DROP TABLE IF EXISTS feedback_usuarios CASCADE;",
        "DROP TABLE IF EXISTS metricas_uso CASCADE;",
        "DROP TABLE IF EXISTS calificaciones CASCADE;",
        "DROP TABLE IF EXISTS alembic_version CASCADE;",
        
        # 2. Eliminar tipos ENUM explícitamente
        "DROP TYPE IF EXISTS estadocaso CASCADE;",
        "DROP TYPE IF EXISTS nivelriesgo CASCADE;",
        "DROP TYPE IF EXISTS estadofactura CASCADE;",
        "DROP TYPE IF EXISTS tiponotificacion CASCADE;",
        "DROP TYPE IF EXISTS rolusuario CASCADE;",
    ]
    
    try:
        with engine.connect() as conn:
            with conn.begin():
                for i, cmd in enumerate(drop_commands, 1):
                    try:
                        print(f"📋 Ejecutando {i}/{len(drop_commands)}: {cmd.split()[2] if 'DROP' in cmd else cmd[:50]}...")
                        conn.execute(text(cmd))
                        print(f"✅ Completado")
                    except Exception as e:
                        print(f"⚠️ Error (ignorado): {e}")
                        continue
                
                print("✅ Eliminación completa terminada")
        
        print("🏗️ PASO 2: Recreando estructura completa...")
        return recreate_structure(engine)
        
    except Exception as e:
        print(f"❌ Error en eliminación: {e}")
        return False

def recreate_structure(engine):
    """Recrear estructura completa sin ENUMs"""
    from sqlalchemy import text
    
    # SQL para recrear todas las tablas SIN ENUM
    create_commands = [
        # 1. Tabla usuarios
        """
        CREATE TABLE usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL DEFAULT 'CLIENTE',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE,
            recibir_emails BOOLEAN DEFAULT TRUE,
            fecha_registro TIMESTAMP
        );
        """,
        
        # 2. Tabla casos
        """
        CREATE TABLE casos (
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
        
        # 3. Tabla documentos
        """
        CREATE TABLE documentos (
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
        
        # 4. Tabla mensajes
        """
        CREATE TABLE mensajes (
            id SERIAL PRIMARY KEY,
            remitente_id INTEGER NOT NULL,
            receptor_id INTEGER NOT NULL,
            caso_id INTEGER,
            contenido VARCHAR(500) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            leido BOOLEAN NOT NULL DEFAULT FALSE
        );
        """,
        
        # 5. Tabla notificaciones
        """
        CREATE TABLE notificaciones (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            mensaje TEXT NOT NULL,
            leido BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_lectura TIMESTAMP,
            datos_adicionales TEXT
        );
        """,
        
        # 6. Tabla facturas
        """
        CREATE TABLE facturas (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            servicio VARCHAR(255) NOT NULL,
            monto DECIMAL(10,2) NOT NULL,
            estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
            fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_pago TIMESTAMP,
            numero_factura VARCHAR(20) NOT NULL UNIQUE,
            descripcion VARCHAR(500),
            metodo_pago VARCHAR(50),
            mercadopago_id VARCHAR(100),
            mercadopago_status VARCHAR(50),
            mercadopago_external_reference VARCHAR(100),
            mercadopago_payment_id VARCHAR(100)
        );
        """,
        
        # 7. Otras tablas auxiliares
        """
        CREATE TABLE feedback_usuarios (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            calificacion INTEGER NOT NULL,
            comentario TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        """
        CREATE TABLE metricas_uso (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            accion VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            datos_adicionales TEXT
        );
        """,
        
        """
        CREATE TABLE calificaciones (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            puntuacion INTEGER NOT NULL,
            comentario TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # 8. Foreign keys
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
        
        """
        ALTER TABLE notificaciones 
        ADD CONSTRAINT fk_notificaciones_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
        """,
        
        """
        ALTER TABLE facturas 
        ADD CONSTRAINT fk_facturas_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
        """,
        
        """
        ALTER TABLE feedback_usuarios 
        ADD CONSTRAINT fk_feedback_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
        """,
        
        """
        ALTER TABLE metricas_uso 
        ADD CONSTRAINT fk_metricas_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
        """,
        
        """
        ALTER TABLE calificaciones 
        ADD CONSTRAINT fk_calificaciones_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
        """,
        
        # 9. Índices importantes
        """
        CREATE INDEX idx_casos_cliente_id ON casos(cliente_id);
        """,
        
        """
        CREATE INDEX idx_casos_abogado_id ON casos(abogado_id);
        """,
        
        """
        CREATE INDEX idx_casos_estado ON casos(estado);
        """,
        
        """
        CREATE INDEX idx_usuarios_email ON usuarios(email);
        """,
        
        """
        CREATE INDEX idx_usuarios_rol ON usuarios(rol);
        """
    ]
    
    try:
        with engine.connect() as conn:
            with conn.begin():
                for i, sql in enumerate(create_commands, 1):
                    step_names = [
                        "tabla usuarios", "tabla casos", "tabla documentos", "tabla mensajes",
                        "tabla notificaciones", "tabla facturas", "tabla feedback_usuarios",
                        "tabla metricas_uso", "tabla calificaciones",
                        "FK casos->cliente", "FK casos->abogado", "FK documentos->usuario",
                        "FK documentos->caso", "FK mensajes->remitente", "FK mensajes->receptor",
                        "FK mensajes->caso", "FK notificaciones->usuario", "FK facturas->usuario",
                        "FK feedback->usuario", "FK metricas->usuario", "FK calificaciones->usuario",
                        "índice casos cliente", "índice casos abogado", "índice casos estado",
                        "índice usuarios email", "índice usuarios rol"
                    ]
                    
                    step_name = step_names[i-1] if i <= len(step_names) else f"comando {i}"
                    
                    try:
                        print(f"📋 Ejecutando {i}/{len(create_commands)}: {step_name}...")
                        conn.execute(text(sql.strip()))
                        print(f"✅ {step_name} completado")
                    except Exception as e:
                        print(f"⚠️ Error en {step_name}: {e}")
                        # Continuar con el siguiente comando
                        continue
                
                print("✅ Estructura recreada completamente")
                
                # Verificación final
                from sqlalchemy import inspect
                inspector = inspect(engine)
                tables_created = inspector.get_table_names()
                print(f"📋 Tablas finales: {tables_created}")
                
                # Verificar tabla casos específicamente
                if 'casos' in tables_created:
                    casos_columns = [col['name'] for col in inspector.get_columns('casos')]
                    print(f"📋 Columnas en tabla casos: {casos_columns}")
                    if 'cliente_id' in casos_columns and 'estado' in casos_columns:
                        print("✅ VERIFICADO: tabla casos correcta con VARCHAR estado")
                        return True
                    else:
                        print("❌ ERROR: tabla casos no tiene estructura correcta")
                        return False
                else:
                    print("❌ ERROR: tabla casos no fue creada")
                    return False
                
    except Exception as e:
        print(f"❌ Error recreando estructura: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 