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
                    "password": "admin123",
                    "nombre": "Administrador",
                    "rol": RolUsuario.ADMIN
                },
                {
                    "email": "abogado@legalassista.com",
                    "password": "abogado123",
                    "nombre": "Abogado Principal",
                    "rol": RolUsuario.ABOGADO
                },
                {
                    "email": "cliente@legalassista.com",
                    "password": "cliente123",
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

def create_users_simple():
    """Método alternativo para crear usuarios usando SQL directo"""
    try:
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        
        print("Usando método alternativo para crear usuarios...")
        engine = create_engine(settings.DATABASE_URL)
        
        # Usuarios con passwords hasheados (bcrypt)
        usuarios_data = [
            ("Admin Test", "admin@legalassista.com", "$2b$12$WOqPY5DBErpluJppclVU0.dm.U1zTWuTKc19k.IHTCgFd9C5ag/ie", "ADMIN"),
            ("Abogado Test", "abogado@legalassista.com", "$2b$12$WOqPY5DBErpluJppclVU0.dm.U1zTWuTKc19k.IHTCgFd9C5ag/ie", "ABOGADO"),
            ("Cliente Test", "cliente@legalassista.com", "$2b$12$SAXakpMz5YSVhxUi5x1zre7SeLVk3IngOEgeGyCpiV1mBcqDN9UFy", "CLIENTE")
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