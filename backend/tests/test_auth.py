import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_register_user(client):
    response = client.post(
        "/api/auth/registro",
        json={
            "email": "test@legalassista.com",
            "password": "test123456",
            "nombre": "Usuario Test",
            "rol": "cliente"
        }
    )
    assert response.status_code == 200
    assert response.json() == "activacion.html"

def test_register_user_invalid_password(client):
    response = client.post(
        "/api/auth/registro",
        json={
            "email": "test@legalassista.com",
            "password": "123",  # Contraseña muy corta
            "nombre": "Usuario Test",
            "rol": "cliente"
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

def test_register_user_invalid_email(client):
    response = client.post(
        "/api/auth/registro",
        json={
            "email": "invalid-email",
            "password": "test123456",
            "nombre": "Usuario Test",
            "rol": "cliente"
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

def test_login_user(client):
    # Primero registramos un usuario
    client.post(
        "/api/auth/registro",
        json={
            "email": "test@legalassista.com",
            "password": "test123456",
            "nombre": "Usuario Test",
            "rol": "cliente"
        }
    )
    
    # Intentamos hacer login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@legalassista.com",
            "password": "test123456"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password(client):
    # Primero registramos un usuario
    client.post(
        "/api/auth/registro",
        json={
            "email": "test@legalassista.com",
            "password": "test123456",
            "nombre": "Usuario Test",
            "rol": "cliente"
        }
    )
    
    # Intentamos hacer login con contraseña incorrecta
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@legalassista.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@legalassista.com",
            "password": "test123456"
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json() 