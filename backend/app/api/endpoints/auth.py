"""
Endpoints de Autenticación
----------------------
Implementa los endpoints para la autenticación y manejo de usuarios.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.core.config import settings
from app.core.security import create_access_token, verify_token, verify_password
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import (
    UsuarioCreate,
    UsuarioResponse,
    Token,
    TokenData,
    RecuperacionPassword
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

router = APIRouter()
auth_service = AuthService()
email_service = EmailService()

@router.post("/registro", response_model=UsuarioResponse)
async def registro(
    user_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario y envía correo de activación.
    """
    try:
        # Registrar usuario
        usuario = await auth_service.registrar_usuario(db, user_data)
        
        # Generar token de activación
        token = create_access_token(
            data={"sub": usuario.email, "tipo": "activacion"},
            expires_delta=timedelta(hours=24)
        )
        
        # Enviar correo de activación
        await email_service.enviar_correo_activacion(
            email=usuario.email,
            nombre=usuario.nombre,
            token=token
        )
        
        return usuario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y retorna un token JWT.
    """
    try:
        # Buscar usuario por email
        usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar contraseña
        if not verify_password(form_data.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar si la cuenta está activa
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta no activada. Por favor, revisa tu correo electrónico."
            )
        
        # Crear token con el ID del usuario en el campo 'sub'
        access_token = create_access_token(
            data={"sub": usuario.id, "email": usuario.email, "rol": usuario.rol.value}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

@router.post("/activar/{token}")
async def activar_cuenta(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Activa la cuenta de un usuario usando el token de activación.
    """
    try:
        # Verificar token
        payload = verify_token(token)
        if payload.get("tipo") != "activacion":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
        
        # Activar usuario
        email = payload.get("sub")
        await auth_service.activar_usuario(db, email)
        
        return {"message": "Cuenta activada exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/recuperar-password")
async def solicitar_recuperacion(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Envía un correo de recuperación de contraseña.
    """
    try:
        # Verificar si el usuario existe
        usuario = await auth_service.obtener_usuario_por_email(db, email)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Generar token de recuperación
        token = create_access_token(
            data={"sub": usuario.email, "tipo": "recuperacion"},
            expires_delta=timedelta(hours=24)
        )
        
        # Enviar correo de recuperación
        await email_service.enviar_correo_recuperacion(
            email=usuario.email,
            token=token
        )
        
        return {"message": "Correo de recuperación enviado"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/restablecer-password")
async def restablecer_password(
    data: RecuperacionPassword,
    db: Session = Depends(get_db)
):
    """
    Restablece la contraseña de un usuario usando el token de recuperación.
    """
    try:
        # Verificar token
        payload = verify_token(data.token)
        if payload.get("tipo") != "recuperacion":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
        
        # Restablecer contraseña
        email = payload.get("sub")
        await auth_service.restablecer_password(
            db,
            email,
            data.nueva_password
        )
        
        return {"message": "Contraseña restablecida exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/perfil", response_model=UsuarioResponse)
async def obtener_perfil(
    current_user: Usuario = Depends(AuthService.get_current_active_user)
):
    """
    Obtiene el perfil del usuario autenticado.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        UsuarioResponse: Datos del usuario
    """
    return current_user 