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

from ...db.database import get_db
from ...schemas.query import UserQuery, QueryResponse, QueryCreate, QueryStatus
from ...schemas.legal_document import SearchQuery
from ...services.search_service import SearchService
from ...services.ai_service import AIService

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
async def get_query(query_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el estado y la respuesta de una consulta existente.
    
    Args:
        query_id: ID único de la consulta
        db: Sesión de base de datos
    
    Returns:
        Estado actual y respuesta de la consulta
    """
    # En una implementación real, se buscaría en la base de datos
    # query = db.query(Query).filter(Query.id == query_id).first()
    # if not query:
    #     raise HTTPException(status_code=404, detail="Consulta no encontrada")
    
    # Para el MVP, simular una respuesta
    return QueryResponse(
        query_id=query_id,
        query_text="¿Cuáles son mis derechos si me despiden sin justa causa?",
        status=QueryStatus.COMPLETED,
        created_at=datetime.now(),
        processed_at=datetime.now(),
        response_text="De acuerdo con la legislación laboral colombiana, si eres despedido sin justa causa...",
        sources=[
            {"id": 1, "title": "Código Sustantivo del Trabajo, Art. 64", "relevance": 0.95},
            {"id": 2, "title": "Sentencia C-1507 de 2000", "relevance": 0.85}
        ],
        confidence_score=0.92,
        needs_human_review=False,
        review_reason=None
    )


async def process_query(query_id: str, query_text: str, db: Session):
    """
    Procesa una consulta en segundo plano.
    
    Args:
        query_id: ID único de la consulta
        query_text: Texto de la consulta
        db: Sesión de base de datos
    """
    try:
        # Actualizar estado a "procesando"
        # db_query = db.query(Query).filter(Query.id == query_id).first()
        # db_query.status = QueryStatus.PROCESSING
        # db.commit()
        
        # Buscar documentos relevantes
        search_results = search_service.search_documents(
            db, 
            SearchQuery(query=query_text, limit=5)
        )
        
        # Obtener documentos de los resultados
        relevant_documents = [result.document for result in search_results]
        
        # Generar respuesta con IA
        response_text, confidence_score, needs_human_review, review_reason = (
            ai_service.generate_response(query_text, relevant_documents)
        )
        
        # Preparar fuentes para la respuesta
        sources = [
            {
                "id": doc.id,
                "title": doc.title,
                "type": doc.document_type,
                "reference": doc.reference_number,
                "relevance": search_results[i].score
            }
            for i, doc in enumerate(relevant_documents)
        ]
        
        # Actualizar estado final
        status = QueryStatus.NEEDS_HUMAN if needs_human_review else QueryStatus.COMPLETED
        
        # En una implementación real, actualizar en la base de datos
        # db_query.status = status
        # db_query.response_text = response_text
        # db_query.sources = json.dumps(sources)
        # db_query.confidence_score = confidence_score
        # db_query.needs_human_review = needs_human_review
        # db_query.review_reason = review_reason
        # db_query.processed_at = datetime.now()
        # db.commit()
        
    except Exception as e:
        # En caso de error, actualizar estado
        # db_query = db.query(Query).filter(Query.id == query_id).first()
        # db_query.status = QueryStatus.ERROR
        # db_query.review_reason = str(e)
        # db.commit()
        pass 