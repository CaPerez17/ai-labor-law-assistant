"""
API de Generación de Contratos
--------------------------
Este módulo implementa los endpoints para generar contratos laborales
a partir de plantillas predefinidas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.schemas.contrato import ContratoInput, ContratoResponse
from app.services.contrato_service import ContratoService

router = APIRouter()
contrato_service = ContratoService()

@router.post("/generar", response_model=ContratoResponse)
async def generar_contrato(
    data: ContratoInput,
    db: Session = Depends(get_db)
) -> ContratoResponse:
    """
    Genera un contrato laboral basado en los datos proporcionados.
    
    Args:
        data: Datos para la generación del contrato
        db: Sesión de base de datos
        
    Returns:
        Contrato generado y metadatos
        
    Raises:
        HTTPException: Si hay un error en la generación
    """
    try:
        resultado = contrato_service.generar_contrato(data)
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el contrato: {str(e)}"
        ) 