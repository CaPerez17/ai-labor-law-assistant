#!/usr/bin/env python3
"""
Test directo de API de autenticación
-----------------------------------
Este script prueba directamente la API de autenticación usando FastAPI TestClient.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configuración de la aplicación - sin conexiones externas
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["FRONTEND_URL"] = "http://localhost:5173"

# Sólo importar las dependencias después de configurar el entorno
from app.db.database import Base
from app.models.usuario import Usuario, RolUsuario
from app.main import app
from app.api.deps import get_db
from app.core.security import get_password_hash

# Crear una base de datos en memoria para las pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Sobrescribir la dependencia para usar la base de datos en memoria
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente de prueba
client = TestClient(app)

def setup_test_db():
    """Crear usuarios de prueba en la base de datos"""
    db = TestingSessionLocal()
    try:
        # Limpiar usuarios existentes
        db.query(Usuario).delete()
        
        # Crear usuarios de prueba
        users = [
            Usuario(
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                nombre="Admin Test",
                rol=RolUsuario.ADMIN,
                activo=True
            ),
            Usuario(
                email="abogado@example.com",
                password_hash=get_password_hash("abogado123"),
                nombre="Abogado Test",
                rol=RolUsuario.ABOGADO,
                activo=True
            ),
            Usuario(
                email="cliente@example.com",
                password_hash=get_password_hash("cliente123"),
                nombre="Cliente Test",
                rol=RolUsuario.CLIENTE,
                activo=True
            )
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        print("✅ Base de datos de prueba configurada")
        
        # Verificar que los usuarios se crearon correctamente
        for email in ["admin@example.com", "abogado@example.com", "cliente@example.com"]:
            user = db.query(Usuario).filter(Usuario.email == email).first()
            if user:
                print(f"  ✓ Usuario {email} creado (rol: {user.rol.value})")
            else:
                print(f"  ✗ Error: Usuario {email} no fue creado")
    
    except Exception as e:
        print(f"❌ Error configurando la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

def test_login():
    """Probar el endpoint de login"""
    print("\n=== PRUEBA DE LOGIN ===")
    
    # Configurar la base de datos de prueba
    setup_test_db()
    
    # Probar login para cada usuario
    for credentials in [
        {"username": "admin@example.com", "password": "admin123"},
        {"username": "abogado@example.com", "password": "abogado123"},
        {"username": "cliente@example.com", "password": "cliente123"}
    ]:
        print(f"\nIntentando login con {credentials['username']}...")
        
        # Intentar login
        response = client.post(
            "/api/auth/login",
            data=credentials,
        )
        
        # Mostrar resultado
        status = response.status_code
        print(f"  Código de estado: {status}")
        
        if status == 200:
            print(f"  ✅ Login exitoso")
            token = response.json().get("access_token")
            print(f"  Token: {token[:20]}...")
            
            # Probar acceso a perfil con el token
            profile_response = client.get(
                "/api/auth/perfil",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if profile_response.status_code == 200:
                print(f"  ✅ Acceso a perfil exitoso")
                user_data = profile_response.json()
                print(f"  Nombre: {user_data.get('nombre')}")
                print(f"  Rol: {user_data.get('rol')}")
            else:
                print(f"  ❌ Error accediendo al perfil: {profile_response.status_code}")
                print(f"  Detalles: {profile_response.text}")
        else:
            print(f"  ❌ Login fallido")
            print(f"  Respuesta: {response.text}")
    
    print("\n=== RESUMEN ===")
    print("Si algún login falló, verifica:")
    print("1. Que las rutas definidas en el router de autenticación sean correctas")
    print("2. Que el método authenticate_user esté definido y funcione correctamente")
    print("3. Que la verificación de contraseñas funcione como se espera")

if __name__ == "__main__":
    test_login() 