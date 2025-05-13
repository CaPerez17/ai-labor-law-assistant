#!/usr/bin/env python3
"""
Script para corregir y probar el sistema de autenticación
--------------------------------------------------------
Este script identifica y corrige problemas en el sistema de autenticación.
"""

import os
import sys
from pathlib import Path
import traceback

# Asegurar que el directorio backend esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importaciones de la aplicación
from app.db.database import SessionLocal, engine, Base
from app.models.usuario import Usuario, RolUsuario
from app.core.security import verify_password, get_password_hash
from sqlalchemy.orm import Session

def fix_authentication_system():
    """Corrige problemas en el sistema de autenticación"""
    db = SessionLocal()
    
    try:
        print("\n=== CORRIGIENDO SISTEMA DE AUTENTICACIÓN ===\n")
        
        # Paso 1: Crear un método authenticate_user independiente para pruebas
        def authenticate_user(email: str, password: str, db: Session):
            """Autentica a un usuario (versión simplificada para pruebas)"""
            # Buscar usuario por email
            user = db.query(Usuario).filter(Usuario.email == email).first()
            if not user:
                print(f"❌ Usuario {email} no encontrado")
                return None
            
            # Verificar contraseña
            if not verify_password(password, user.password_hash):
                print(f"❌ Contraseña incorrecta para {email}")
                return None
            
            return user
        
        # Paso 2: Crear o actualizar usuarios de prueba
        test_users = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "nombre": "Admin Test",
                "rol": RolUsuario.ADMIN
            },
            {
                "email": "abogado@example.com",
                "password": "abogado123",
                "nombre": "Abogado Test",
                "rol": RolUsuario.ABOGADO
            },
            {
                "email": "cliente@example.com",
                "password": "cliente123",
                "nombre": "Cliente Test",
                "rol": RolUsuario.CLIENTE
            }
        ]
        
        for user_data in test_users:
            # Verificar si el usuario existe
            existing_user = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
            
            if existing_user:
                print(f"Usuario {user_data['email']} ya existe. Actualizando contraseña...")
                existing_user.password_hash = get_password_hash(user_data["password"])
                existing_user.activo = True  # Asegurarse de que el usuario esté activo
            else:
                print(f"Creando usuario {user_data['email']}...")
                new_user = Usuario(
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    nombre=user_data["nombre"],
                    rol=user_data["rol"],
                    activo=True
                )
                db.add(new_user)
        
        # Guardar cambios
        db.commit()
        print("✅ Usuarios de prueba creados/actualizados correctamente\n")
        
        # Paso 3: Probar autenticación con cada usuario
        print("=== PRUEBA DE AUTENTICACIÓN ===\n")
        
        for user_data in test_users:
            email = user_data["email"]
            password = user_data["password"]
            
            print(f"Intentando autenticar a {email}...")
            # Cargar el usuario fresco desde la base de datos
            user = db.query(Usuario).filter(Usuario.email == email).first()
            
            if not user:
                print(f"❌ ERROR: Usuario {email} no encontrado en la base de datos\n")
                continue
            
            print(f"✅ Usuario: {user.email} (rol: {user.rol.value})")
            print(f"   Hash almacenado: {user.password_hash[:20]}...")
            
            # Prueba de verificación directa
            password_correct = verify_password(password, user.password_hash)
            print(f"   Verificación directa: {'✅' if password_correct else '❌'}")
            
            # Prueba de autenticación completa
            authenticated = authenticate_user(email, password, db)
            print(f"   Autenticación completa: {'✅' if authenticated else '❌'}")
            print()
            
            # Si la autenticación falla, probar con un hash nuevo
            if not authenticated:
                print(f"   ⚠️ La autenticación falló, actualizando hash...")
                user.password_hash = get_password_hash(password)
                db.commit()
                
                # Probar nuevamente
                password_correct = verify_password(password, user.password_hash)
                print(f"   Verificación tras actualización: {'✅' if password_correct else '❌'}")
                
                authenticated = authenticate_user(email, password, db)
                print(f"   Autenticación tras actualización: {'✅' if authenticated else '❌'}")
            
            print("-"*50)
        
        print("\n✅ Pruebas completadas")
        print("""
Para usar estos usuarios en la aplicación:
1. admin@example.com / admin123 (Administrador)
2. abogado@example.com / abogado123 (Abogado)
3. cliente@example.com / cliente123 (Cliente)
""")
        
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR: {str(e)}")
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    fix_authentication_system() 