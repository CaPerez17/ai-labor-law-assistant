import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.notificacion import Notificacion, TipoNotificacion
from app.models.usuario import Usuario, RolUsuario
from app.core.auth import create_access_token
from app.db.session import get_db

client = TestClient(app)

def test_crear_notificacion(db: Session):
    # Crear usuario de prueba
    usuario = Usuario(
        email="test@example.com",
        nombre="Usuario Test",
        password_hash="hashed_password",
        rol=RolUsuario.CLIENTE
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Crear token de acceso
    token = create_access_token({"sub": usuario.email})

    # Crear notificación
    notificacion_data = {
        "tipo": TipoNotificacion.MENSAJE,
        "titulo": "Test Notificación",
        "mensaje": "Este es un mensaje de prueba",
        "datos_adicionales": {"test": "data"}
    }

    response = client.post(
        "/api/notificaciones/",
        json=notificacion_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == notificacion_data["titulo"]
    assert data["mensaje"] == notificacion_data["mensaje"]
    assert data["tipo"] == notificacion_data["tipo"]

def test_obtener_notificaciones(db: Session):
    # Crear usuario de prueba
    usuario = Usuario(
        email="test2@example.com",
        nombre="Usuario Test 2",
        password_hash="hashed_password",
        rol=RolUsuario.CLIENTE
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Crear algunas notificaciones
    notificaciones = [
        Notificacion(
            usuario_id=usuario.id,
            tipo=TipoNotificacion.MENSAJE,
            titulo=f"Test {i}",
            mensaje=f"Mensaje de prueba {i}",
            leido=i % 2 == 0
        )
        for i in range(3)
    ]
    db.add_all(notificaciones)
    db.commit()

    # Crear token de acceso
    token = create_access_token({"sub": usuario.email})

    # Obtener notificaciones
    response = client.get(
        "/api/notificaciones/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_marcar_como_leida(db: Session):
    # Crear usuario de prueba
    usuario = Usuario(
        email="test3@example.com",
        nombre="Usuario Test 3",
        password_hash="hashed_password",
        rol=RolUsuario.CLIENTE
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Crear notificación
    notificacion = Notificacion(
        usuario_id=usuario.id,
        tipo=TipoNotificacion.MENSAJE,
        titulo="Test",
        mensaje="Mensaje de prueba",
        leido=False
    )
    db.add(notificacion)
    db.commit()
    db.refresh(notificacion)

    # Crear token de acceso
    token = create_access_token({"sub": usuario.email})

    # Marcar como leída
    response = client.post(
        f"/api/notificaciones/{notificacion.id}/marcar-leida",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["leido"] == True
    assert data["fecha_lectura"] is not None 