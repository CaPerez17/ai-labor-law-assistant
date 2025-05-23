"""
Endpoints de Abogados
------------------
Implementa los endpoints para la gestión de casos por abogados.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.abogado import (
    CasoAbogado,
    UpdateCasoInput,
    CasoResponse,
    EstadoCaso,
    NivelRiesgo
)
from app.services.abogado_service import AbogadoService
from app.db.session import get_db

router = APIRouter()
abogado_service = AbogadoService()

@router.get("/casos", response_model=List[CasoAbogado])
async def obtener_casos(
    estado: Optional[EstadoCaso] = Query(None, description="Filtrar por estado del caso"),
    nivel_riesgo: Optional[NivelRiesgo] = Query(None, description="Filtrar por nivel de riesgo"),
    db: Session = Depends(get_db)
) -> List[CasoAbogado]:
    """
    Obtiene la lista de casos con filtros opcionales.
    
    Args:
        estado: Filtrar por estado del caso
        nivel_riesgo: Filtrar por nivel de riesgo
        db: Sesión de base de datos
        
    Returns:
        Lista de casos que coinciden con los filtros
    """
    try:
        return abogado_service.obtener_casos(estado, nivel_riesgo)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener casos: {str(e)}"
        )

@router.get("/casos/{id_caso}", response_model=CasoAbogado)
async def obtener_caso(
    id_caso: str,
    db: Session = Depends(get_db)
) -> CasoAbogado:
    """
    Obtiene un caso específico por su ID.
    
    Args:
        id_caso: ID del caso a obtener
        db: Sesión de base de datos
        
    Returns:
        Caso encontrado
        
    Raises:
        HTTPException: Si el caso no existe
    """
    caso = abogado_service.obtener_caso(id_caso)
    if not caso:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el caso con ID {id_caso}"
        )
    return caso

@router.post("/actualizar", response_model=CasoResponse)
async def actualizar_caso(
    data: UpdateCasoInput,
    db: Session = Depends(get_db)
) -> CasoResponse:
    """
    Actualiza el estado y comentarios de un caso.
    
    Args:
        data: Datos para actualizar el caso
        db: Sesión de base de datos
        
    Returns:
        Respuesta con el resultado de la actualización
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        return abogado_service.actualizar_caso(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar caso: {str(e)}"
        ) 