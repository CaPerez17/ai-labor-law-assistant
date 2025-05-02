"""
API de Búsqueda Optimizada
-----------------------
Este módulo define las rutas API para realizar búsquedas optimizadas en documentos legales
utilizando el servicio BM25 mejorado para la integración con la base de datos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import time
from datetime import datetime

from app.db.database import get_db
from app.models.legal_document import DocumentType
from app.schemas.legal_document import SearchQuery
from app.services.optimized_bm25_service import OptimizedBM25Service


# Esquemas de respuesta específicos para el endpoint de búsqueda
class SearchResultItem(BaseModel):
    """Esquema para un item de resultado de búsqueda"""
    document_id: int = Field(..., description="ID del documento")
    title: str = Field(..., description="Título del documento")
    reference_number: str = Field(..., description="Número de referencia del documento")
    document_type: str = Field(..., description="Tipo de documento")
    relevance_score: float = Field(..., description="Puntuación de relevancia")
    snippet: str = Field(..., description="Fragmento relevante del documento")
    cached: bool = Field(False, description="Indica si el resultado proviene del caché")


class SearchResponse(BaseModel):
    """Esquema para la respuesta de búsqueda"""
    query: str = Field(..., description="Consulta realizada")
    cached: bool = Field(False, description="Indica si la respuesta completa proviene del caché")
    results: List[SearchResultItem] = Field(default_factory=list, description="Resultados de la búsqueda")
    processing_time_ms: Optional[float] = Field(None, description="Tiempo de procesamiento en milisegundos")
    document_count: Optional[int] = Field(None, description="Número de documentos indexados")
    timestamp: str = Field(..., description="Marca de tiempo de la consulta")


# Crear router y servicio de búsqueda optimizado
router = APIRouter()
bm25_service = OptimizedBM25Service(
    k1=1.5,  # Parámetro de saturación de término
    b=0.75,  # Parámetro de normalización de longitud
    use_cache=True
)


@router.post("/", response_model=SearchResponse)
def search(
    query: str = Query(..., min_length=3, description="Texto de la consulta"),
    document_type: Optional[str] = Query(None, description="Tipo de documento a filtrar"),
    category: Optional[str] = Query(None, description="Categoría a filtrar"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de resultados"),
    force_reindex: bool = Query(False, description="Forzar reconstrucción del índice BM25"),
    db: Session = Depends(get_db)
):
    """
    Realiza una búsqueda optimizada en los documentos legales utilizando BM25.
    
    Args:
        query: Texto de la consulta
        document_type: Tipo de documento a filtrar (opcional)
        category: Categoría a filtrar (opcional)
        limit: Número máximo de resultados
        force_reindex: Forzar reconstrucción del índice BM25
        db: Sesión de base de datos
    
    Returns:
        Respuesta con los resultados de búsqueda más relevantes
    """
    # Validar la consulta
    if not query or len(query.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La consulta debe tener al menos 3 caracteres"
        )
    
    # Validar tipo de documento si se especificó
    doc_type = None
    if document_type:
        try:
            doc_type = DocumentType(document_type.lower())
        except ValueError:
            valid_types = [t.value for t in DocumentType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de documento inválido. Valores válidos: {', '.join(valid_types)}"
            )
    
    # Crear objeto de consulta
    search_query = SearchQuery(
        query=query,
        document_type=doc_type,
        category=category,
        limit=limit
    )
    
    # Forzar reconstrucción del índice si se solicitó
    if force_reindex:
        bm25_service.force_reindex(db)
    
    # Iniciar tiempo para medición de rendimiento
    start_time = time.time()
    
    # Realizar la búsqueda optimizada
    search_results = bm25_service.search_documents(db, search_query)
    
    # Calcular tiempo de procesamiento en milisegundos
    processing_time = (time.time() - start_time) * 1000
    
    # Determinar si algún resultado proviene del caché
    is_cached = any(result.get("cached", False) for result in search_results)
    
    # Obtener estado del índice
    index_status = bm25_service.index_status()
    
    # Formatear la respuesta según el esquema requerido
    response = {
        "query": query,
        "cached": is_cached,
        "results": search_results,
        "processing_time_ms": round(processing_time, 2),
        "document_count": index_status.get("document_count", 0),
        "timestamp": datetime.now().isoformat()
    }
    
    return response


@router.get("/status", response_model=Dict[str, Any])
def get_index_status(db: Session = Depends(get_db)):
    """
    Obtiene información sobre el estado del índice BM25.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Información sobre el estado del índice BM25
    """
    # Si el índice no está inicializado, intentar construirlo
    if not bm25_service._bm25_index:
        bm25_service._build_index(db)
        
    # Obtener estado del índice
    status = bm25_service.index_status()
    
    # Agregar información adicional
    status["document_types"] = [t.value for t in DocumentType]
    status["db_url"] = str(db.bind.url).replace("***", "[REDACTED]")
    status["timestamp"] = datetime.now().isoformat()
    
    return status 