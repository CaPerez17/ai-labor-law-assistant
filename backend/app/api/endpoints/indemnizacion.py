"""
API de Cálculo de Indemnización
---------------------------
Este módulo implementa los endpoints para calcular indemnizaciones
por despido según la legislación laboral colombiana.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from db.database import get_db
from schemas.indemnizacion import DespidoInput, IndemnizacionResponse
from services.indemnizacion_service import IndemnizacionService

router = APIRouter()
indemnizacion_service = IndemnizacionService()

@router.post("/calcular", response_model=IndemnizacionResponse)
async def calcular_indemnizacion(
    data: DespidoInput,
    db: Session = Depends(get_db)
) -> IndemnizacionResponse:
    """
    Calcula la indemnización por despido basado en los datos proporcionados.
    
    Args:
        data: Datos del despido a analizar
        db: Sesión de base de datos
        
    Returns:
        Resultado del cálculo con detalles y recomendaciones
        
    Raises:
        HTTPException: Si hay un error en el cálculo
    """
    try:
        resultado = indemnizacion_service.calcular_indemnizacion(data)
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular la indemnización: {str(e)}"
        ) 