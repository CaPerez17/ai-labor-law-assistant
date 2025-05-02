"""
Endpoint de Escalamiento a Abogados
--------------------------------
Este módulo implementa el endpoint para el proceso de escalamiento
de casos a abogados humanos.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from schemas.escalamiento import EscalamientoInput, EscalamientoResponse
from services.escalamiento_service import EscalamientoService
from db.session import get_db

router = APIRouter()
escalamiento_service = EscalamientoService()

@router.post("/escalar", response_model=EscalamientoResponse)
async def escalar_caso(
    input_data: EscalamientoInput,
    db: Session = Depends(get_db)
) -> Any:
    """
    Escala un caso a un abogado humano.
    
    Args:
        input_data: Datos del caso a escalar
        db: Sesión de base de datos
        
    Returns:
        Respuesta con el resultado del escalamiento
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        return escalamiento_service.escalar_caso(input_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al escalar el caso: {str(e)}"
        ) 