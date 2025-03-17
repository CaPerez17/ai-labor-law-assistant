"""
Endpoint de Consultas Legales Directas
----------------------------------
Este módulo implementa un endpoint directo para consultas al asistente legal,
que combina la búsqueda BM25 con la generación de respuestas con GPT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from ...db.database import get_db
from ...schemas.legal_document import SearchQuery
from ...schemas.query import LegalResponse
from ...services.search_service import SearchService
from ...services.ai_service import AIService

router = APIRouter()
search_service = SearchService()
ai_service = AIService()

class LegalQuery(BaseModel):
    """Esquema para consultas legales directas"""
    query: str = Field(..., min_length=5, description="Consulta legal del usuario")

@router.post("/", response_model=LegalResponse)
async def ask_legal_question(
    query: LegalQuery,
    db: Session = Depends(get_db)
):
    """
    Endpoint para realizar consultas legales directas.
    
    Este endpoint combina la búsqueda de documentos relevantes con BM25
    y la generación de respuestas fundamentadas con GPT.
    
    Args:
        query: Consulta del usuario
        db: Sesión de base de datos
    
    Returns:
        Respuesta legal con referencias a documentos utilizados
    """
    try:
        # 1. Buscar documentos relevantes con BM25
        search_query = SearchQuery(query=query.query, limit=5)
        search_results = search_service.search_documents(db, search_query)
        
        if not search_results:
            return LegalResponse(
                query=query.query,
                response="No se encontraron documentos legales relevantes para responder a tu consulta. Por favor, intenta reformular tu pregunta o consulta con un abogado especializado.",
                references=[],
                confidence_score=0.0,
                processing_time_ms=0,
                timestamp=datetime.now().isoformat()
            )
        
        # 2. Generar respuesta con GPT utilizando los documentos relevantes
        start_time = datetime.now()
        response_text, confidence_score, needs_human_review, review_reason = ai_service.generate_response(
            query_text=query.query,
            search_results=search_results,
            threshold=0.7
        )
        
        # 3. Formatear respuesta con fuentes
        formatted_response = ai_service.format_response_with_sources(response_text, search_results)
        
        # 4. Calcular tiempo de procesamiento
        end_time = datetime.now()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # 5. Preparar respuesta final
        return LegalResponse(
            query=query.query,
            response=formatted_response["response_text"],
            references=formatted_response["sources"],
            confidence_score=confidence_score,
            needs_human_review=needs_human_review,
            review_reason=review_reason if needs_human_review else None,
            processing_time_ms=round(processing_time_ms, 2),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la consulta: {str(e)}"
        ) 