#!/usr/bin/env python3
"""
Script para depurar el sistema de autenticación
-----------------------------------------------
Este script prueba la autenticación con distintos usuarios.
"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio backend esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importaciones de la aplicación
from app.db.database import SessionLocal, engine, Base
from app.models.usuario import Usuario, RolUsuario
from app.services.auth_service import AuthService
from app.core.security import verify_password, get_password_hash
from sqlalchemy.orm import Session

def debug_authentication():
    """Prueba el proceso de autenticación paso a paso"""
    db = SessionLocal()
    
    try:
        # Credenciales de prueba (basadas en los usuarios seed)
        test_emails = [
            "admin@legalassista.com",
            "abogado@legalassista.com"
        ]
        test_password = "admin123"  # Contraseña para todos los usuarios de prueba
        
        print("\n--- DEPURACIÓN DE AUTENTICACIÓN ---\n")
        
        # Verificar si los usuarios existen
        for email in test_emails:
            user = db.query(Usuario).filter(Usuario.email == email).first()
            
            if not user:
                print(f"❌ ERROR: El usuario {email} no existe en la base de datos")
                continue
            
            print(f"✅ Usuario encontrado: {user.email} (rol: {user.rol.value})")
            print(f"   Nombre: {user.nombre}")
            print(f"   Activo: {user.activo}")
            print(f"   Hash de contraseña: {user.password_hash[:25]}...")
            
            # Intentar verificar la contraseña
            password_matches = verify_password(test_password, user.password_hash)
            print(f"   ¿Contraseña coincide?: {'✅' if password_matches else '❌'}")
            
            if not password_matches:
                # Probemos con AuthService
                auth_verify = AuthService.verify_password(test_password, user.password_hash)
                print(f"   Verificación usando AuthService: {'✅' if auth_verify else '❌'}")
                
                # Generemos un nuevo hash para comparar
                new_hash = get_password_hash(test_password)
                print(f"   Nuevo hash generado: {new_hash[:25]}...")
                
                # POSIBLE ERROR: auth.py usa autenticar_usuario, pero AuthService.py no tiene esta función
                # Lo que haría authenticate_user:
                user_auth = AuthService.authenticate_user(email, test_password, db)
                print(f"   Autenticación completa: {'✅ Éxito' if user_auth else '❌ Fallo'}")
            
            print("\n" + "-"*50 + "\n")
        
        # Si ningún usuario existe, creemos uno de prueba
        if db.query(Usuario).count() == 0:
            print("No hay usuarios en la base de datos. Creando usuario de prueba...")
            
            # Crear un hash usando la función correcta
            hashed_password = get_password_hash(test_password)
            
            test_user = Usuario(
                email="test@example.com",
                password_hash=hashed_password,
                nombre="Usuario de Prueba",
                rol=RolUsuario.ADMIN,
                activo=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ Usuario de prueba creado: {test_user.email}")
            print(f"   Contraseña en texto plano: {test_password}")
            print(f"   Hash generado: {test_user.password_hash[:25]}...")
        
    except Exception as e:
        print(f"❌ ERROR durante la depuración: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_authentication() 