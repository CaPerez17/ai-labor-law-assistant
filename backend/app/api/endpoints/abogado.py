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
    UpdateCasoInput,
    CasoResponse,
    EstadoCaso,
    NivelRiesgo
)
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
        logger.info(f"Obteniendo casos para abogado: {current_user.email}")
        
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Solo abogados pueden acceder a esta función."
            )
        
        # Query base para casos del abogado
        query = db.query(Caso).filter(Caso.abogado_id == current_user.id)
        
        # Aplicar filtro por estado si se proporciona
        if estado:
            try:
                estado_enum = EstadoCaso(estado)
                query = query.filter(Caso.estado == estado_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {estado}"
                )
        
        casos = query.all()
        
        logger.info(f"Encontrados {len(casos)} casos para el abogado")
        
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
            caso.estado = EstadoCaso(caso_update.estado)
        
        if caso_update.comentarios:
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
            Caso.estado == EstadoCaso.PENDIENTE
        ).count()
        casos_resueltos = db.query(Caso).filter(
            Caso.abogado_id == current_user.id,
            Caso.estado == EstadoCaso.RESUELTO
        ).count()
        
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