import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import get_current_active_user, create_access_token
from app.models.usuario import Usuario
from app.core.config import settings
from app.db.session import get_db
from jose import jwt
import asyncio

class MockQuery:
    def __init__(self, usuarios):
        self.usuarios = usuarios
    
    def filter(self, condition):
        # Simular filter basado en email
        return self
    
    def first(self):
        # Devolver el primer usuario (o None si no hay)
        return self.usuarios[0] if self.usuarios else None

class MockDB:
    def __init__(self, usuarios):
        self.usuarios = usuarios
    
    def query(self, model):
        return MockQuery(self.usuarios)

@pytest.mark.asyncio
async def test_get_current_active_user_valid():
    """Test con usuario activo y token válido"""
    user = Usuario(
        id=1,
        email="test@example.com", 
        nombre="Test User", 
        activo=True,
        rol="CLIENTE"
    )
    token = create_access_token({"sub": user.email})
    mock_db = MockDB([user])
    
    result = await get_current_active_user(token, mock_db)
    assert result.email == user.email
    assert result.activo is True

@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """Test con usuario inactivo"""
    user = Usuario(
        id=2,
        email="inactive@example.com", 
        nombre="Inactive User", 
        activo=False,
        rol="CLIENTE"
    )
    token = create_access_token({"sub": user.email})
    mock_db = MockDB([user])
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(token, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Inactive user" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_current_active_user_invalid_token():
    """Test con token inválido"""
    mock_db = MockDB([])
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user("token_invalido", mock_db)
    
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_active_user_user_not_found():
    """Test cuando el usuario no existe"""
    token = create_access_token({"sub": "nonexistent@example.com"})
    mock_db = MockDB([])  # Base de datos vacía
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(token, mock_db)
    
    assert exc_info.value.status_code == 401 