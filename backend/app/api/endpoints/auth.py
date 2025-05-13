"""
Endpoints de Autenticación
----------------------
Implementa los endpoints para la autenticación y manejo de usuarios.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import os
import logging

from app.core.config import settings
from app.core.security import create_access_token, verify_token, verify_password, get_password_hash
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

# Configurar logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y retorna un token JWT.
    
    Devuelve:
    - Un token de acceso JWT si las credenciales son válidas
    - Mensajes de error específicos si falla la autenticación
    """
    try:
        # Log de la solicitud entrante
        body = await request.json()
        logger.info(f"Intento de login: endpoint=/api/auth/login, método={request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Body recibido: {body}")
        
        # Obtener email y password (permitir tanto username como email)
        email = form_data.username  # OAuth2PasswordRequestForm usa username
        if 'email' in body:
            email = body['email']  # Si hay un campo 'email' en el body, úsalo
            logger.info(f"Usando email del body JSON: {email}")
        
        password = form_data.password
        if 'password' in body:
            password = body['password']
            logger.info(f"Usando password del body JSON (no logueado por seguridad)")
        
        logger.info(f"Autenticando usuario con email: {email}")
        
        # Verificar si estamos en modo demo
        demo_mode = os.environ.get("LEGALASSISTA_DEMO", "").lower() == "true"
        logger.info(f"Modo demo activado: {demo_mode}")
        
        # En modo demo, intentar modificar el nombre de usuario para usar la versión demo
        if demo_mode and not email.endswith("_demo@legalassista.com"):
            # Extraer el rol de la dirección de correo si es posible
            if "@" in email:
                username_parts = email.split("@")[0]
                # Si el usuario ya tiene un formato como "admin@", "cliente@", etc.
                if any(role in username_parts.lower() for role in ["admin", "abogado", "cliente"]):
                    for role in ["admin", "abogado", "cliente"]:
                        if role in username_parts.lower():
                            demo_username = f"{role}_demo@legalassista.com"
                            break
                else:
                    # Si no se puede determinar el rol, usar cliente por defecto
                    demo_username = "cliente_demo@legalassista.com"
            else:
                # Si no tiene formato de correo, usar cliente demo
                demo_username = "cliente_demo@legalassista.com"
                
            logger.info(f"Modo demo activado. Usuario original: {email}, Usuario demo: {demo_username}")
            email = demo_username
            password = "demo123"  # Contraseña estándar para usuarios demo
        
        # Buscar usuario por email
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            logger.error(f"Usuario no encontrado: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo no registrado en LegalAssista"
            )
        
        logger.info(f"Usuario encontrado: {email}, rol: {usuario.rol.value}")
        
        # Verificar contraseña
        password_valid = verify_password(password, usuario.password_hash)
        logger.info(f"Contraseña válida: {password_valid}")
        
        if not password_valid:
            logger.error(f"Contraseña incorrecta para usuario: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta"
            )
        
        # Verificar si la cuenta está activa
        if not usuario.activo:
            logger.error(f"Cuenta no activada: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta no activada. Por favor, revisa tu correo electrónico para activarla."
            )
        
        # Crear token con el ID del usuario en el campo 'sub'
        access_token = create_access_token(
            data={
                "sub": usuario.id, 
                "email": usuario.email, 
                "rol": usuario.rol.value,
                "demo": demo_mode
            }
        )
        
        logger.info(f"Token generado exitosamente para usuario: {email}")
        
        # Construir respuesta con usuario
        user_data = {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "role": usuario.rol.value
        }
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": user_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error de autenticación: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error al procesar la solicitud de autenticación: {str(e)}"
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