from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.security import get_current_active_user
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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crea una nueva notificación.
    
    Args:
        notificacion: Datos de la notificación
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene las notificaciones del usuario actual.
    
    Args:
        solo_no_leidas: Si es True, solo devuelve notificaciones no leídas
        limite: Número máximo de notificaciones a devolver
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cuenta las notificaciones no leídas del usuario actual.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        dict: Número de notificaciones no leídas
    """
    count = await notificacion_service.contar_no_leidas(db, current_user.id)
    return {"count": count}

@router.post("/{notificacion_id}/marcar-leida", response_model=NotificacionResponse)
async def marcar_como_leida(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Marca una notificación como leída.
    
    Args:
        notificacion_id: ID de la notificación
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Marca todas las notificaciones del usuario como leídas.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        dict: Número de notificaciones marcadas como leídas
    """
    count = await notificacion_service.marcar_todas_como_leidas(db, current_user.id)
    return {"count": count}

@router.get("/{notificacion_id}", response_model=NotificacionResponse)
async def obtener_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una notificación específica del usuario actual.
    
    Args:
        notificacion_id: ID de la notificación
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        NotificacionResponse: Notificación obtenida
    """
    notificacion = await notificacion_service.obtener_notificacion(
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

@router.delete("/{notificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina una notificación específica del usuario actual.
    
    Args:
        notificacion_id: ID de la notificación
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        None: Notificación eliminada exitosamente
    """
    if not await notificacion_service.eliminar_notificacion(
        db=db,
        notificacion_id=notificacion_id,
        usuario_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    return None 