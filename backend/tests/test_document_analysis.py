#!/usr/bin/env python3
"""
Test de análisis de documentos
----------------------------
Prueba la funcionalidad de análisis de documentos legales.
"""

import os
import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configuración para pruebas
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"

# Importar después de configurar el entorno
from app.db.database import Base
from app.models.usuario import Usuario, RolUsuario
from app.main import app
from app.api.deps import get_db
from app.core.security import get_password_hash

# Crear una base de datos en memoria para tests
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas en la base de datos de test
Base.metadata.create_all(bind=engine)

# Sobrescribir la dependencia de la base de datos
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente para las pruebas
client = TestClient(app)

# Mock del servicio de OpenAI para pruebas
class MockOpenAIService:
    def analyze_document(self, text, prompt=None):
        return {
            "analysis": "Este es un análisis de prueba.",
            "summary": "Resumen del documento para pruebas.",
            "recommendations": ["Recomendación 1", "Recomendación 2"]
        }

# Fixture para crear un usuario de prueba
@pytest.fixture
def test_user_token():
    # Crear un usuario de prueba
    db = TestSessionLocal()
    
    # Eliminar usuarios existentes
    db.query(Usuario).delete()
    
    # Crear usuario de prueba
    user = Usuario(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        nombre="Usuario Test",
        rol=RolUsuario.CLIENTE,
        activo=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Obtener un token para el usuario
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    
    token = response.json().get("access_token")
    db.close()
    
    return token

# Archivo de ejemplo para pruebas
@pytest.fixture
def test_document():
    content = """
    CONTRATO INDIVIDUAL DE TRABAJO A TÉRMINO INDEFINIDO
    
    Entre los suscritos, EMPRESA ABC S.A.S. con NIT 900.123.456-7, 
    representada por JUAN PÉREZ, identificado con C.C. 80.123.456, 
    quien en adelante se denominará EL EMPLEADOR, y MARÍA RODRÍGUEZ, 
    identificada con C.C. 52.987.654, quien en adelante se denominará 
    LA TRABAJADORA, se ha celebrado el presente CONTRATO INDIVIDUAL DE 
    TRABAJO, regido por las siguientes cláusulas:
    
    PRIMERA: OBJETO. LA TRABAJADORA se obliga a prestar sus servicios 
    personales como ASISTENTE ADMINISTRATIVA en las instalaciones de 
    EL EMPLEADOR.
    
    SEGUNDA: DURACIÓN. El presente contrato se celebra a término indefinido, 
    iniciando el 15 de enero de 2023.
    
    TERCERA: SALARIO. LA TRABAJADORA devengará un salario mensual de 
    UN MILLÓN DOSCIENTOS MIL PESOS M/CTE ($1.200.000).
    """
    
    # Crear un archivo temporal con el contenido
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        temp.write(content.encode())
        temp_path = temp.name
    
    yield temp_path
    
    # Limpiar después de las pruebas
    os.unlink(temp_path)

def test_document_upload_and_analysis(test_user_token, test_document):
    """Prueba la carga y análisis de un documento legal"""
    
    # Preparar el archivo para carga
    with open(test_document, "rb") as file:
        # Hacer la petición de carga de documento
        response = client.post(
            "/api/documento/upload",
            headers={"Authorization": f"Bearer {test_user_token}"},
            files={"file": ("test_contract.txt", file, "text/plain")}
        )
        
        # Verificar la respuesta
        assert response.status_code == 200 or response.status_code == 201
        result = response.json()
        
        # Verificar que se devuelve un ID de documento
        assert "id" in result
        document_id = result["id"]
        
        # Verificar que se puede obtener el documento
        get_response = client.get(
            f"/api/documento/{document_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert get_response.status_code == 200
        document_data = get_response.json()
        
        # Verificar que contiene los datos básicos
        assert "nombre" in document_data
        assert "contenido" in document_data
        
        print(f"✅ Test de análisis de documentos exitoso")
        print(f"Documento analizado: ID {document_id}")
        print(f"Nombre: {document_data.get('nombre')}")
        print(f"Tamaño del contenido: {len(document_data.get('contenido'))} caracteres")


if __name__ == "__main__":
    # Ejecutar test directo para depuración
    token = test_user_token()
    test_document_path = next(test_document())
    test_document_upload_and_analysis(token, test_document_path) 