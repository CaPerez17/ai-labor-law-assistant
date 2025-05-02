"""

Fixtures para pruebas
------------------
Define los fixtures comunes para todas las pruebas.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app
from app.core.config import settings
from app.api.deps import get_db

# Importar todos los modelos para asegurar que SQLAlchemy los registre
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion
from app.models.caso import Caso
from app.models.documento import Documento
from app.models.feedback_usuario import FeedbackUsuario
from app.models.calificacion import Calificacion
from app.models.metrica_uso import MetricaUso
from app.models.mensaje import Mensaje
from app.models.factura import Factura

# Crear motor de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una nueva sesión para cada prueba
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Limpiar después de cada prueba
    session.close()
    transaction.rollback()
    connection.close()
    
    # Eliminar todas las tablas después de cada prueba
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app) 