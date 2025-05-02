"""
API de Consultas de Usuarios
--------------------------
Este módulo define las rutas API para manejar las consultas de usuarios.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from app.db.database import get_db
from app.schemas.query import UserQuery, QueryResponse, QueryCreate, QueryStatus
from app.schemas.legal_document import SearchQuery
from app.services.search_service import SearchService
from app.services.ai_service import AIService

router = APIRouter()
search_service = SearchService()
ai_service = AIService()

@router.post("/", response_model=QueryResponse)
async def create_query(
    query: UserQuery,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva consulta y programa su procesamiento en segundo plano.
    
    Args:
        query: Datos de la consulta del usuario
        background_tasks: Tareas en segundo plano de FastAPI
        db: Sesión de base de datos
    
    Returns:
        Respuesta inicial con el ID de la consulta
    """
    # Generar ID único para la consulta
    query_id = str(uuid.uuid4())
    
    # Crear respuesta inicial
    response = QueryResponse(
        query_id=query_id,
        query_text=query.query_text,
        status=QueryStatus.PENDING,
        created_at=datetime.now(),
        response_text=None,
        sources=None,
        confidence_score=None,
        needs_human_review=False,
        review_reason=None
    )
    
    # Guardar la consulta en la base de datos (en una implementación real)
    # db_query = Query(id=query_id, text=query.query_text, ...)
    # db.add(db_query)
    # db.commit()
    
    # Programar el procesamiento en segundo plano
    background_tasks.add_task(process_query, query_id, query.query_text, db)
    
    return response


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query_status(query_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el estado de una consulta existente.
    
    Args:
        query_id: ID único de la consulta
        db: Sesión de base de datos
    
    Returns:
        Estado actual de la consulta
    """
    # En una implementación real, buscaríamos la consulta en la base de datos
    # query = db.query(Query).filter(Query.id == query_id).first()
    # if not query:
    #     raise HTTPException(status_code=404, detail="Consulta no encontrada")
    
    # Aquí simularemos una respuesta para el MVP
    return QueryResponse(
        query_id=query_id,
        query_text="¿Cuántos días de licencia de maternidad me corresponden?",
        status=QueryStatus.COMPLETED,
        created_at=datetime.now(),
        processed_at=datetime.now(),
        response_text="Según la legislación colombiana actual, la licencia de maternidad es de 18 semanas...",
        sources=[
            {"id": 1, "title": "Código Sustantivo del Trabajo, Artículo 236", "relevance": 0.92},
            {"id": 4, "title": "Sentencia C-005 de 2017", "relevance": 0.78}
        ],
        confidence_score=0.89,
        needs_human_review=False,
        review_reason=None
    )


async def process_query(query_id: str, query_text: str, db: Session):
    """
    Procesa una consulta y genera una respuesta basada en documentos relevantes.
    
    Args:
        query_id: ID único de la consulta
        query_text: Texto de la consulta
        db: Sesión de base de datos
    """
    try:
        # En una implementación real, actualizaríamos el estado en la base de datos
        # db_query = db.query(Query).filter(Query.id == query_id).first()
        # db_query.status = QueryStatus.PROCESSING
        # db.commit()
        
        # 1. Buscar documentos relevantes con BM25
        search_query = SearchQuery(query=query_text, limit=5)
        search_results = search_service.search_documents(db, search_query)
        
        if not search_results:
            # No se encontraron documentos relevantes
            # En una implementación real, actualizaríamos la consulta en la base de datos
            # db_query.status = QueryStatus.COMPLETED
            # db_query.response_text = "No se encontraron documentos relevantes para tu consulta."
            # db_query.confidence_score = 0.0
            # db_query.needs_human_review = True
            # db_query.review_reason = "No se encontraron documentos relevantes"
            # db_query.processed_at = datetime.now()
            # db.commit()
            return
        
        # 2. Generar respuesta con GPT utilizando los documentos relevantes
        response_text, confidence_score, needs_human_review, review_reason = ai_service.generate_response(
            query_text=query_text,
            search_results=search_results,
            threshold=0.7  # Umbral de confianza para requerir revisión humana
        )
        
        # 3. Formatear la respuesta con fuentes
        formatted_response = ai_service.format_response_with_sources(response_text, search_results)
        
        # 4. En una implementación real, actualizaríamos la consulta en la base de datos
        # db_query.status = QueryStatus.NEEDS_HUMAN if needs_human_review else QueryStatus.COMPLETED
        # db_query.response_text = response_text
        # db_query.sources = formatted_response["sources"]
        # db_query.confidence_score = confidence_score
        # db_query.needs_human_review = needs_human_review
        # db_query.review_reason = review_reason
        # db_query.processed_at = datetime.now()
        # db.commit()
        
    except Exception as e:
        # En caso de error, actualizaríamos la consulta en la base de datos
        # db_query.status = QueryStatus.ERROR
        # db_query.review_reason = f"Error al procesar la consulta: {str(e)}"
        # db_query.needs_human_review = True
        # db_query.processed_at = datetime.now()
        # db.commit()
        print(f"Error al procesar consulta {query_id}: {str(e)}")


@router.post("/sync", response_model=QueryResponse)
async def process_query_sync(query: UserQuery, db: Session = Depends(get_db)):
    """
    Procesa una consulta de forma síncrona y devuelve la respuesta inmediatamente.
    Útil para propósitos de prueba o consultas que requieren respuesta inmediata.
    
    Args:
        query: Datos de la consulta del usuario
        db: Sesión de base de datos
    
    Returns:
        Respuesta completa con la información generada
    """
    # Generar ID único para la consulta
    query_id = str(uuid.uuid4())
    created_at = datetime.now()
    
    try:
        # 1. Buscar documentos relevantes con BM25
        search_query = SearchQuery(query=query.query_text, limit=5)
        search_results = search_service.search_documents(db, search_query)
        
        if not search_results:
            # No se encontraron documentos relevantes
            return QueryResponse(
                query_id=query_id,
                query_text=query.query_text,
                status=QueryStatus.COMPLETED,
                created_at=created_at,
                processed_at=datetime.now(),
                response_text="No se encontraron documentos relevantes para tu consulta.",
                sources=[],
                confidence_score=0.0,
                needs_human_review=True,
                review_reason="No se encontraron documentos relevantes"
            )
        
        # 2. Generar respuesta con GPT utilizando los documentos relevantes
        response_text, confidence_score, needs_human_review, review_reason = ai_service.generate_response(
            query_text=query.query_text,
            search_results=search_results,
            threshold=0.7
        )
        
        # 3. Formatear la respuesta con fuentes
        formatted_response = ai_service.format_response_with_sources(response_text, search_results)
        
        # 4. Crear y devolver la respuesta
        return QueryResponse(
            query_id=query_id,
            query_text=query.query_text,
            status=QueryStatus.NEEDS_HUMAN if needs_human_review else QueryStatus.COMPLETED,
            created_at=created_at,
            processed_at=datetime.now(),
            response_text=formatted_response["response_text"],
            sources=formatted_response["sources"],
            confidence_score=confidence_score,
            needs_human_review=needs_human_review,
            review_reason=review_reason
        )
        
    except Exception as e:
        # En caso de error, devolver respuesta con detalles del error
        return QueryResponse(
            query_id=query_id,
            query_text=query.query_text,
            status=QueryStatus.ERROR,
            created_at=created_at,
            processed_at=datetime.now(),
            response_text="Lo siento, ocurrió un error al procesar tu consulta.",
            sources=[],
            confidence_score=0.0,
            needs_human_review=True,
            review_reason=f"Error: {str(e)}"
        ) 