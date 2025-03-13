"""
API de Búsqueda
-----------
Este módulo define las rutas API para realizar búsquedas en documentos legales.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from ...db.database import get_db
from ...models.legal_document import DocumentType
from ...schemas.legal_document import SearchQuery
from ...services.search_service import SearchService


# Esquemas de respuesta específicos para el endpoint de búsqueda
class SearchResultItem(BaseModel):
    """Esquema para un item de resultado de búsqueda"""
    document_id: int = Field(..., description="ID del documento")
    title: str = Field(..., description="Título del documento")
    reference_number: str = Field(..., description="Número de referencia del documento")
    document_type: DocumentType = Field(..., description="Tipo de documento")
    relevance_score: float = Field(..., description="Puntuación de relevancia")
    snippet: str = Field(..., description="Fragmento relevante del documento")
    cached: bool = Field(False, description="Indica si el resultado proviene del caché")


class SearchResponse(BaseModel):
    """Esquema para la respuesta de búsqueda"""
    query: str = Field(..., description="Consulta realizada")
    cached: bool = Field(False, description="Indica si la respuesta completa proviene del caché")
    results: List[SearchResultItem] = Field(default_factory=list, description="Resultados de la búsqueda")
    processing_time_ms: Optional[float] = Field(None, description="Tiempo de procesamiento en milisegundos")


router = APIRouter()
search_service = SearchService()


@router.post("/", response_model=SearchResponse)
def search(search_query: SearchQuery, db: Session = Depends(get_db)):
    """
    Realiza una búsqueda en los documentos legales utilizando BM25.
    
    Args:
        search_query: Parámetros de búsqueda
        db: Sesión de base de datos
    
    Returns:
        Respuesta con los resultados de búsqueda más relevantes
    """
    # Validar entrada
    if not search_query.query or len(search_query.query.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La consulta debe tener al menos 3 caracteres"
        )
    
    # Iniciar tiempo para medición de rendimiento
    import time
    start_time = time.time()
    
    # Realizar la búsqueda
    search_results = search_service.search_documents(db, search_query)
    
    # Calcular tiempo de procesamiento en milisegundos
    processing_time = (time.time() - start_time) * 1000
    
    # Determinar si algún resultado proviene del caché
    is_cached = any(result.get("cached", False) for result in search_results)
    
    # Formatear la respuesta según el esquema requerido
    response = {
        "query": search_query.query,
        "cached": is_cached,
        "results": search_results,
        "processing_time_ms": round(processing_time, 2)
    }
    
    return response 