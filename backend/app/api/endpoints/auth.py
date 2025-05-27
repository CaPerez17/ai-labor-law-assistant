"""
Endpoints de Autenticación
----------------------
Implementa los endpoints para la autenticación y manejo de usuarios.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
import logging
import json
import sys

from app.core.config import settings
from app.core.security import create_access_token, verify_token, verify_password, get_password_hash
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import (
    UsuarioCreate,
    UsuarioResponse,
    Token,
    TokenData,
    RecuperacionPassword,
    UserData
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.core.registry import registry

# Configurar logger con nivel de debug para máxima información
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log inicial para diagnóstico
logger.info("Cargando módulo de autenticación auth.py")
logger.info(f"Versión de Python: {sys.version}")
logger.info(f"Ruta del sistema: {sys.path}")

# Verificar que registry esté configurado
if not registry.is_configured:
    logger.warning("Registry no configurado al cargar endpoints de autenticación")
    registry.configure()
    logger.info("Registry configurado desde auth.py")
else:
    logger.info("Registry ya estaba configurado")

router = APIRouter()
logger.info("Router de autenticación creado correctamente")

# Inicialización de servicios
# Intentar obtener auth_service desde registry o crear uno nuevo
auth_service = registry.get_service("auth_service")
if auth_service is None:
    logger.warning("No se encontró auth_service en registry, creando nueva instancia")
    auth_service = AuthService()
else:
    logger.info("Usando auth_service desde registry")

# Intentar obtener email_service desde registry o crear uno nuevo
email_service = registry.get_service("email_service")
if email_service is None:
    logger.warning("No se encontró email_service en registry, creando nueva instancia")
    email_service = EmailService()
    registry.register_service("email_service", email_service)
else:
    logger.info("Usando email_service desde registry")

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
        
        # Intentar enviar correo de activación
        try:
            await email_service.enviar_correo_activacion(
                email=usuario.email,
                nombre=usuario.nombre,
                token=token
            )
            logger.info(f"✅ Correo de activación enviado a {usuario.email}")
        except Exception as email_error:
            logger.warning(f"⚠️ No se pudo enviar correo de activación: {email_error}")
            # No fallar el registro si el email no se puede enviar
        
        return usuario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/status")
async def auth_status():
    """
    Endpoint simple para verificar que la ruta de autenticación está disponible.
    Útil para depuración y monitoreo.
    """
    logger.info("Endpoint de estado de autenticación accedido")
    return {
        "status": "online",
        "message": "El servicio de autenticación está funcionando correctamente",
        "endpoints": {
            "login": "/api/auth/login",
            "registro": "/api/auth/registro",
            "activar": "/api/auth/activar/{token}",
            "recuperar-password": "/api/auth/recuperar-password",
            "perfil": "/api/auth/perfil"
        }
    }

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
    - Datos del usuario autenticado en formato compatible con el frontend
    """
    try:
        # Log de la solicitud entrante
        logger.info(f"🔑 [Auth] Recibiendo solicitud de login")
        
        # Obtener email y password
        email = form_data.username
        password = form_data.password
        
        logger.info(f"🔑 [Auth] Intentando autenticar usuario: {email}")
        
        # Buscar usuario por email
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            logger.error(f"❌ [Auth] Usuario no encontrado: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar contraseña
        password_valid = verify_password(password, usuario.password_hash)
        logger.info(f"🔑 [Auth] Validación de contraseña: {'✅' if password_valid else '❌'}")
        
        if not password_valid:
            logger.error(f"❌ [Auth] Contraseña incorrecta para usuario: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar si la cuenta está activa
        if not usuario.activo:
            logger.error(f"❌ [Auth] Cuenta no activada: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta no activada. Por favor, revisa tu correo electrónico."
            )
        
        # Crear token con el ID del usuario
        access_token = create_access_token(
            data={
                "sub": str(usuario.id),
                "email": usuario.email,
                "rol": usuario.rol.value
            }
        )
        
        logger.info(f"✅ [Auth] Login exitoso para {email}")
        
        # Construir objeto UserData para respuesta
        user_data = UserData(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            role=usuario.rol.value
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [Auth] Error interno: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
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
        
        # Intentar enviar correo de recuperación
        try:
            await email_service.enviar_correo_recuperacion(
                email=usuario.email,
                token=token
            )
            logger.info(f"✅ Correo de recuperación enviado a {usuario.email}")
            return {"message": "Correo de recuperación enviado"}
        except Exception as email_error:
            logger.warning(f"⚠️ No se pudo enviar correo de recuperación: {email_error}")
            return {
                "message": "Token de recuperación generado", 
                "token": token,
                "note": "El servicio de email no está disponible. Usa este token para restablecer tu contraseña."
            }
        
    except HTTPException:
        raise
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