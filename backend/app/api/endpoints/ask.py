"""
Endpoint de Consultas Legales Directas
----------------------------------
Este módulo implementa un endpoint directo para consultas al asistente legal,
que combina la búsqueda BM25 con la generación de respuestas con GPT.
Incluye optimizaciones para reducir consumo de tokens y controles de uso.
"""

import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Dict, Any
import hashlib

from app.db.database import get_db
from app.schemas.legal_document import SearchQuery
from app.schemas.query import LegalResponse
from app.services.search_service import SearchService
from app.services.ai_service import AIService
import sys
from pathlib import Path

# Asegurar que backend/ esté en sys.path para poder importar el módulo config
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from config import DAILY_QUERY_LIMIT, ECONOMY_MODE

router = APIRouter()
search_service = SearchService()
ai_service = AIService()

# Control de uso diario
usage_file = os.path.join(backend_dir, "usage_stats.json")

def get_daily_usage() -> int:
    """Obtiene el uso diario actual"""
    today = date.today().isoformat()
    try:
        if os.path.exists(usage_file):
            with open(usage_file, 'r', encoding='utf-8') as f:
                usage_data = json.load(f)
                return usage_data.get(today, 0)
        return 0
    except Exception as e:
        print(f"Error al leer estadísticas de uso: {str(e)}")
        return 0

def increment_daily_usage() -> None:
    """Incrementa el contador de uso diario"""
    today = date.today().isoformat()
    try:
        usage_data = {}
        if os.path.exists(usage_file):
            with open(usage_file, 'r', encoding='utf-8') as f:
                usage_data = json.load(f)
        
        usage_data[today] = usage_data.get(today, 0) + 1
        
        with open(usage_file, 'w', encoding='utf-8') as f:
            json.dump(usage_data, f, indent=2)
    except Exception as e:
        print(f"Error al actualizar estadísticas de uso: {str(e)}")

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
        # Verificar límite diario
        daily_usage = get_daily_usage()
        if daily_usage >= DAILY_QUERY_LIMIT:
            return LegalResponse(
                query=query.query,
                response="Has alcanzado el límite diario de consultas. Por favor, intenta de nuevo mañana.",
                references=[],
                confidence_score=0.0,
                needs_human_review=True,
                review_reason="Límite diario excedido",
                processing_time_ms=0,
                timestamp=datetime.now().isoformat()
            )
        
        # Incrementar contador de uso
        increment_daily_usage()
        
        # 1. Buscar documentos relevantes con BM25 (limitados según configuración)
        search_query = SearchQuery(query=query.query, limit=5)  # Primero buscamos 5 y luego filtramos
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