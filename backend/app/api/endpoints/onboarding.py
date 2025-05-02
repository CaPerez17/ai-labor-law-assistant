"""
Endpoint de Onboarding Conversacional
---------------------------------
Este módulo implementa el endpoint para el proceso de onboarding
que analiza las necesidades del usuario y recomienda el flujo más apropiado.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from schemas.onboarding import OnboardingInput, OnboardingResponse
from services.onboarding_service import OnboardingService
from db.session import get_db

router = APIRouter()
onboarding_service = OnboardingService()

@router.post("/analizar", response_model=OnboardingResponse)
async def analizar_necesidad(
    input_data: OnboardingInput,
    db: Session = Depends(get_db)
) -> Any:
    """
    Analiza la necesidad del usuario y recomienda el flujo más apropiado.
    
    Args:
        input_data: Datos de entrada con el texto de la consulta
        db: Sesión de base de datos
        
    Returns:
        Respuesta con el flujo recomendado y pasos a seguir
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        return onboarding_service.analizar_necesidad(input_data.free_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la necesidad: {str(e)}"
        ) 