"""
API de Análisis de Contrato Realidad
---------------------------------
Este módulo implementa los endpoints para analizar la existencia
de un contrato realidad según la jurisprudencia colombiana.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from db.database import get_db
from schemas.contrato_realidad import ContratoRealidadInput, ContratoRealidadResponse
from services.contrato_realidad_service import ContratoRealidadService

router = APIRouter()
contrato_service = ContratoRealidadService()

@router.post("/analizar", response_model=ContratoRealidadResponse)
async def analizar_contrato_realidad(
    data: ContratoRealidadInput,
    db: Session = Depends(get_db)
) -> ContratoRealidadResponse:
    """
    Analiza si existe un contrato realidad basado en los datos proporcionados.
    
    Args:
        data: Datos del contrato a analizar
        db: Sesión de base de datos
        
    Returns:
        Resultado del análisis con nivel de riesgo y recomendaciones
    """
    try:
        resultado = contrato_service.evaluar_contrato_realidad(data)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar el contrato: {str(e)}"
        ) 