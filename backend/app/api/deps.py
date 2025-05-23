from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Usuario:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
        
        # Intentar obtener "sub" como ID primero
        user_id = token_data.sub
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token inválido o expirado",
            )
            
        # Si el sub parece ser un email (contiene @), buscar por email
        if isinstance(user_id, str) and '@' in user_id:
            user = db.query(Usuario).filter(Usuario.email == user_id).first()
        else:
            # De lo contrario, buscar por ID
            user = db.query(Usuario).filter(Usuario.id == user_id).first()
            
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo validar las credenciales",
        )
        
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user 