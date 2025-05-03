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

# Importaciones de la aplicación
from app.db.database import SessionLocal, engine, Base
from app.models.usuario import Usuario, RolUsuario
from app.services.auth_service import AuthService
from sqlalchemy.orm import Session

def create_initial_users():
    """
    Crea usuarios iniciales si no existen:
    - admin@legalassista.com (administrador)
    - abogado@legalassista.com (abogado)
    """
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
            hashed_password = AuthService.get_password_hash(user_data["password"])
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
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando script de inicialización de usuarios...")
    create_initial_users()
    print("Proceso finalizado.") 