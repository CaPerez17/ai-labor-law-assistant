"""
Endpoints de Métricas y Feedback
----------------------------
Este módulo implementa los endpoints para el registro de métricas
y feedback de los usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict
from pathlib import Path

from schemas.metricas import MetricaUso, FeedbackUsuario, FeedbackResponse
from services.metricas_service import MetricasService
from db.session import get_db

router = APIRouter()
metricas_service = MetricasService()

@router.post("/metricas/registrar")
async def registrar_metrica(
    metrica: MetricaUso,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Registra una métrica de uso.
    
    Args:
        metrica: Datos de la métrica a registrar
        db: Sesión de base de datos
        
    Returns:
        Mensaje de confirmación
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        metricas_service.registrar_metrica(metrica)
        return {"mensaje": "Métrica registrada exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar la métrica: {str(e)}"
        )

@router.post("/feedback/enviar", response_model=FeedbackResponse)
async def enviar_feedback(
    feedback: FeedbackUsuario,
    db: Session = Depends(get_db)
) -> Any:
    """
    Registra el feedback de un usuario.
    
    Args:
        feedback: Datos del feedback a registrar
        db: Sesión de base de datos
        
    Returns:
        Respuesta con mensaje de confirmación
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        return metricas_service.registrar_feedback(feedback)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar el feedback: {str(e)}"
        )

@router.get("/metricas/estadisticas")
async def obtener_estadisticas(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de uso y feedback.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Estadísticas de uso y feedback
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        return metricas_service.obtener_estadisticas()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@router.get("/metricas/exportar")
async def exportar_metricas(
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Exporta las métricas a un archivo CSV.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Mensaje con la ruta del archivo exportado
        
    Raises:
        HTTPException: Si hay un error al procesar la solicitud
    """
    try:
        ruta_archivo = Path("data/metricas/metricas_exportadas.csv")
        metricas_service.exportar_metricas_csv(str(ruta_archivo))
        return {"mensaje": f"Métricas exportadas a {ruta_archivo}"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar métricas: {str(e)}"
        ) 