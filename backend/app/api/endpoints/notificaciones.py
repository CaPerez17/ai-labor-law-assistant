from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion, TipoNotificacion
from app.services.notificacion_service import NotificacionService
from app.schemas.notificacion import NotificacionResponse, NotificacionCreate

router = APIRouter()
notificacion_service = NotificacionService()

@router.post("/", response_model=NotificacionResponse)
async def crear_notificacion(
    notificacion: NotificacionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva notificación.
    
    Args:
        notificacion: Datos de la notificación
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        NotificacionResponse: Notificación creada
    """
    return await notificacion_service.crear_notificacion(
        db=db,
        usuario_id=current_user.id,
        tipo=notificacion.tipo,
        titulo=notificacion.titulo,
        mensaje=notificacion.mensaje,
        datos_adicionales=notificacion.datos_adicionales
    )

@router.get("/", response_model=List[NotificacionResponse])
async def obtener_notificaciones(
    solo_no_leidas: bool = False,
    limite: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las notificaciones del usuario actual.
    
    Args:
        solo_no_leidas: Si es True, solo devuelve notificaciones no leídas
        limite: Número máximo de notificaciones a devolver
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        List[NotificacionResponse]: Lista de notificaciones
    """
    return await notificacion_service.obtener_notificaciones(
        db=db,
        usuario_id=current_user.id,
        solo_no_leidas=solo_no_leidas,
        limite=limite
    )

@router.get("/contar-no-leidas")
async def contar_no_leidas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cuenta las notificaciones no leídas del usuario actual.
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Número de notificaciones no leídas
    """
    count = await notificacion_service.contar_no_leidas(db, current_user.id)
    return {"count": count}

@router.post("/{notificacion_id}/marcar-leida", response_model=NotificacionResponse)
async def marcar_como_leida(
    notificacion_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marca una notificación como leída.
    
    Args:
        notificacion_id: ID de la notificación
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        NotificacionResponse: Notificación actualizada
    """
    notificacion = await notificacion_service.marcar_como_leida(
        db=db,
        notificacion_id=notificacion_id,
        usuario_id=current_user.id
    )
    
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    return notificacion

@router.post("/marcar-todas-leidas")
async def marcar_todas_como_leidas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marca todas las notificaciones del usuario como leídas.
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Número de notificaciones marcadas como leídas
    """
    count = await notificacion_service.marcar_todas_como_leidas(db, current_user.id)
    return {"count": count} 