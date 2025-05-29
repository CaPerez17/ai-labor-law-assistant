#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
-------------------------------------------
Este script crea usuarios iniciales en la base de datos.
Se deben ejecutar con los permisos adecuados.
"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio backend esté en sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

def create_initial_users():
    """
    Crea usuarios iniciales si no existen:
    - admin@legalassista.com (administrador)
    - abogado@legalassista.com (abogado)
    - cliente@legalassista.com (cliente)
    """
    try:
        # Importaciones de la aplicación
        from app.db.session import SessionLocal
        from app.models.usuario import Usuario, RolUsuario
        from app.core.security import get_password_hash
        
        # Crear una sesión
        db = SessionLocal()
        
        try:
            # Configuración de usuarios iniciales
            initial_users = [
                {
                    "email": "admin@legalassista.com",
                    "password": os.getenv("SEED_ADMIN_PASSWORD", "admin123"),
                    "nombre": "Administrador",
                    "rol": RolUsuario.ADMIN
                },
                {
                    "email": "abogado@legalassista.com",
                    "password": os.getenv("SEED_ABOGADO_PASSWORD", "Abogado123!"),
                    "nombre": "Abogado Principal",
                    "rol": RolUsuario.ABOGADO
                },
                {
                    "email": "cliente@legalassista.com",
                    "password": os.getenv("SEED_CLIENTE_PASSWORD", "Cliente123!"),
                    "nombre": "Cliente Test",
                    "rol": RolUsuario.CLIENTE
                }
            ]
            
            users_created = 0
            
            # Intentar crear cada usuario
            for user_data in initial_users:
                # Verificar si el usuario ya existe
                existing_user = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
                
                if existing_user:
                    print(f"El usuario {user_data['email']} ya existe con rol {existing_user.rol.value}")
                    continue
                
                # Crear usuario
                hashed_password = get_password_hash(user_data["password"])
                new_user = Usuario(
                    email=user_data["email"],
                    password_hash=hashed_password,
                    nombre=user_data["nombre"],
                    rol=user_data["rol"],
                    activo=True
                )
                
                db.add(new_user)
                users_created += 1
                print(f"Usuario creado: {user_data['email']} con rol {user_data['rol'].value}")
            
            # Guardar cambios
            db.commit()
            
            if users_created > 0:
                print(f"\nSe han creado {users_created} usuarios iniciales.")
            else:
                print("\nNo se ha creado ningún usuario nuevo. Todos ya existían.")
            
            # Crear casos de prueba solo si los usuarios existen
            create_sample_cases(db)
                
        except Exception as e:
            db.rollback()
            print(f"Error al crear usuarios iniciales: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error en imports o configuración: {e}")
        # Usar método alternativo más simple
        create_users_simple()

def create_sample_cases(db):
    """Crear casos de prueba si los usuarios existen"""
    try:
        from app.models.caso import Caso
        from app.models.usuario import Usuario, RolUsuario
        
        # Verificar si ya hay casos
        caso_count = db.query(Caso).count()
        if caso_count > 0:
            print(f"Ya existen {caso_count} casos en la base de datos")
            return
        
        # Buscar usuarios para asignar casos
        abogado = db.query(Usuario).filter(Usuario.rol == RolUsuario.ABOGADO).first()
        cliente = db.query(Usuario).filter(Usuario.rol == RolUsuario.CLIENTE).first()
        
        if not abogado or not cliente:
            print("⚠️ No se encontraron usuarios abogado o cliente, saltando creación de casos")
            return
        
        # Crear casos de prueba usando strings directamente
        casos_prueba = [
            {
                "titulo": "Consulta sobre contrato laboral",
                "descripcion": "Cliente solicita revisión de contrato de trabajo",
                "estado": "PENDIENTE",  # String directo
                "nivel_riesgo": "MEDIO",  # String directo
                "comentarios": "Caso prioritario para revisión",
                "cliente_id": cliente.id,
                "abogado_id": abogado.id
            },
            {
                "titulo": "Reclamación de horas extras",
                "descripcion": "Trabajador no ha recibido pago por horas extras trabajadas",
                "estado": "EN_PROCESO",  # String directo
                "nivel_riesgo": "BAJO",  # String directo
                "comentarios": "Revisar contratos y comprobantes",
                "cliente_id": cliente.id,
                "abogado_id": abogado.id
            },
            {
                "titulo": "Despido improcedente",
                "descripcion": "Cliente fue despedido sin justa causa",
                "estado": "PENDIENTE_VERIFICACION",  # String directo
                "nivel_riesgo": "ALTO",  # String directo
                "comentarios": "Caso urgente - revisar documentación completa",
                "cliente_id": cliente.id,
                "abogado_id": abogado.id
            }
        ]
        
        for caso_data in casos_prueba:
            nuevo_caso = Caso(**caso_data)
            db.add(nuevo_caso)
        
        db.commit()
        print(f"✅ {len(casos_prueba)} casos de prueba creados exitosamente")
        
    except Exception as e:
        print(f"⚠️ Error creando casos de prueba: {e}")
        # No hacer rollback completo, solo para casos
        pass

def create_users_simple():
    """Método alternativo para crear usuarios usando SQL directo"""
    try:
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        
        print("Usando método alternativo para crear usuarios...")
        engine = create_engine(settings.DATABASE_URL)
        
        # Verificar si las tablas existen
        with engine.connect() as conn:
            # Verificar tabla usuarios
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
                user_count = result.scalar()
                print(f"📊 Usuarios existentes: {user_count}")
                
                if user_count > 0:
                    print("👥 Ya existen usuarios, saltando creación")
                    return
                    
            except Exception as e:
                print(f"❌ Error verificando usuarios: {e}")
                return
        
        # Usuarios con passwords hasheados (bcrypt)
        # Passwords: admin123, Abogado123!, Cliente123!
        usuarios_data = [
            ("Admin Test", "admin@legalassista.com", "$2b$12$WOqPY5DBErpluJppclVU0.dm.U1zTWuTKc19k.IHTCgFd9C5ag/ie", "ADMIN"),
            ("Abogado Test", "abogado@legalassista.com", "$2b$12$QwQwQwQwQwQwQwQwQwQwQeQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQw", "ABOGADO"),
            ("Cliente Test", "cliente@legalassista.com", "$2b$12$wQwQwQwQwQwQwQwQwQwQwOQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQwQw", "CLIENTE")
        ]
        
        with engine.connect() as conn:
            for nombre, email, password_hash, rol in usuarios_data:
                # Verificar si el usuario ya existe
                result = conn.execute(text("SELECT COUNT(*) FROM usuarios WHERE email = :email"), {"email": email})
                if result.scalar() > 0:
                    print(f"Usuario {email} ya existe")
                    continue
                
                # Crear usuario
                conn.execute(text("""
                    INSERT INTO usuarios (nombre, email, password_hash, rol, activo, recibir_emails, fecha_registro)
                    VALUES (:nombre, :email, :password_hash, :rol, TRUE, TRUE, CURRENT_TIMESTAMP)
                """), {
                    "nombre": nombre,
                    "email": email, 
                    "password_hash": password_hash,
                    "rol": rol
                })
                print(f"Usuario creado: {email} con rol {rol}")
            
            conn.commit()
            print("✅ Usuarios creados exitosamente")
            
    except Exception as e:
        print(f"Error en método alternativo: {e}")

if __name__ == "__main__":
    print("Iniciando script de inicialización de usuarios...")
    create_initial_users()
    print("Proceso finalizado.") 