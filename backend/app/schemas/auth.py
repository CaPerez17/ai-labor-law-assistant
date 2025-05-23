"""
Schemas de Autenticación
--------------------
Define los modelos Pydantic para la autenticación y manejo de usuarios.
"""

from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.usuario import RolUsuario

class UsuarioBase(BaseModel):
    """Modelo base para usuarios"""
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    rol: RolUsuario

class UsuarioCreate(UsuarioBase):
    """Modelo para crear un usuario"""
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_min_length(cls, v):
        """Valida la fortaleza de la contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UsuarioLogin(BaseModel):
    """Modelo para login de usuario"""
    email: EmailStr
    password: str

class UsuarioResponse(UsuarioBase):
    """Modelo para respuesta de usuario"""
    id: int
    activo: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True

class UserData(BaseModel):
    """Datos básicos del usuario para el frontend"""
    id: int
    email: EmailStr
    nombre: str
    role: str  # Usa 'role' en lugar de 'rol' para compatibilidad con el frontend

class Token(BaseModel):
    """Modelo para token JWT"""
    access_token: str
    token_type: str
    user: Optional[UserData] = None

class TokenData(BaseModel):
    """Modelo para datos del token"""
    sub: Optional[int] = None
    email: Optional[str] = None

class RecuperacionPassword(BaseModel):
    email: EmailStr
    token: Optional[str] = None
    nueva_password: Optional[str] = None

    @validator('nueva_password')
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserBase(BaseModel):
    email: EmailStr
    nombre: str
    activo: Optional[bool] = True
    recibir_emails: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    rol: str

    class Config:
        from_attributes = True 