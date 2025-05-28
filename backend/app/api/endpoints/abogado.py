"""
Endpoints de Abogados
------------------
Implementa los endpoints para la gestión de casos por abogados.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.schemas.abogado import (
    CasoAbogado,
    UpdateCasoInput
)
from app.schemas.caso import CasoResponse
from app.services.abogado_service import AbogadoService
from app.db.session import get_db
from app.models.usuario import Usuario
from app.models.caso import Caso
from app.schemas.caso import CasoUpdate
from app.services.auth_service import AuthService
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()
abogado_service = AbogadoService()

@router.get("/casos", response_model=List[CasoResponse])
async def obtener_casos_abogado(
    estado: Optional[str] = Query(None, description="Filtrar por estado del caso"),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los casos asignados al abogado actual
    """
    try:
        logger.info(f"Obteniendo casos para abogado: {current_user.email} con filtro de estado: {estado}")
        
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Solo abogados pueden acceder a esta función."
            )
        
        # Query base para casos del abogado
        query = db.query(Caso).filter(Caso.abogado_id == current_user.id)
        
        # Aplicar filtro por estado si se proporciona y es un string válido
        if estado:
            # Validar que el estado sea uno de los permitidos si es necesario,
            # o simplemente usar el string directamente si el frontend ya envía valores válidos.
            # Por ahora, usaremos el string directamente.
            logger.debug(f"Aplicando filtro de estado: {estado}")
            query = query.filter(Caso.estado == estado)
        
        casos = query.all()
        
        logger.info(f"Encontrados {len(casos)} casos para el abogado {current_user.email}")
        
        # Si no hay casos, devolver lista vacía en lugar de error
        return casos
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo casos del abogado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/casos/{caso_id}", response_model=CasoResponse)
async def obtener_caso_detalle(
    caso_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un caso específico del abogado
    """
    try:
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado"
            )
        
        # Buscar el caso
        caso = db.query(Caso).filter(
            Caso.id == caso_id,
            Caso.abogado_id == current_user.id
        ).first()
        
        if not caso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        return caso
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalle del caso {caso_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/casos/{caso_id}", response_model=CasoResponse)
async def actualizar_caso(
    caso_id: int,
    caso_update: CasoUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de un caso
    """
    try:
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado"
            )
        
        # Buscar el caso
        caso = db.query(Caso).filter(
            Caso.id == caso_id,
            Caso.abogado_id == current_user.id
        ).first()
        
        if not caso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        # Actualizar campos
        if caso_update.estado:
            logger.debug(f"Actualizando estado del caso {caso_id} a: {caso_update.estado}")
            caso.estado = caso_update.estado # Asignar string directamente
        
        if caso_update.comentarios:
            logger.debug(f"Actualizando comentarios del caso {caso_id}")
            caso.comentarios = caso_update.comentarios
        
        db.commit()
        db.refresh(caso)
        
        logger.info(f"Caso {caso_id} actualizado por abogado {current_user.email}")
        
        return caso
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando caso {caso_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/metricas")
async def obtener_metricas_abogado(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene métricas específicas del abogado
    """
    try:
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado"
            )
        
        # Calcular métricas
        total_casos = db.query(Caso).filter(Caso.abogado_id == current_user.id).count()
        casos_pendientes = db.query(Caso).filter(
            Caso.abogado_id == current_user.id,
            Caso.estado == "PENDIENTE"  # Comparar con string
        ).count()
        casos_resueltos = db.query(Caso).filter(
            Caso.abogado_id == current_user.id,
            Caso.estado == "RESUELTO"  # Comparar con string
        ).count()
        
        logger.info(f"Métricas para abogado {current_user.email}: Total={total_casos}, Pendientes={casos_pendientes}, Resueltos={casos_resueltos}")
        
        return {
            "total_casos": total_casos,
            "casos_pendientes": casos_pendientes,
            "casos_resueltos": casos_resueltos,
            "tasa_resolucion": (casos_resueltos / total_casos * 100) if total_casos > 0 else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo métricas del abogado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 