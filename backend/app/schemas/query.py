"""
Esquemas para Consultas de Usuarios
---------------------------------
Este módulo define los esquemas Pydantic para la validación y serialización
de consultas de usuarios y respuestas del sistema.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QueryStatus(str, Enum):
    """Estados posibles para una consulta de usuario"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    NEEDS_HUMAN = "needs_human"
    ERROR = "error"


class QuerySource(str, Enum):
    """Fuentes posibles para una consulta de usuario"""
    WEB = "web"
    WHATSAPP = "whatsapp"
    API = "api"


class UserQuery(BaseModel):
    """Esquema para consultas de usuarios"""
    query_text: str = Field(..., min_length=5, description="Texto de la consulta del usuario")
    source: QuerySource = Field(default=QuerySource.WEB, description="Fuente de la consulta")
    user_id: Optional[str] = Field(None, description="ID del usuario si está autenticado")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")


class QueryResponseBase(BaseModel):
    """Esquema base para respuestas a consultas"""
    query_id: str = Field(..., description="ID único de la consulta")
    query_text: str = Field(..., description="Texto original de la consulta")
    status: QueryStatus = Field(..., description="Estado de la consulta")
    created_at: datetime = Field(..., description="Fecha y hora de creación")
    processed_at: Optional[datetime] = Field(None, description="Fecha y hora de procesamiento")


class QueryResponse(QueryResponseBase):
    """Esquema completo para respuestas a consultas"""
    response_text: Optional[str] = Field(None, description="Texto de la respuesta generada")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Fuentes utilizadas")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Puntuación de confianza")
    needs_human_review: bool = Field(False, description="Indica si requiere revisión humana")
    review_reason: Optional[str] = Field(None, description="Razón por la que requiere revisión")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query_id": "550e8400-e29b-41d4-a716-446655440000",
                "query_text": "¿Cuántos días de licencia de maternidad me corresponden?",
                "status": "completed",
                "created_at": "2023-01-01T12:00:00",
                "processed_at": "2023-01-01T12:00:05",
                "response_text": "Según la legislación colombiana actual, la licencia de maternidad es de 18 semanas...",
                "sources": [
                    {"id": 24, "title": "Ley 1822 de 2017", "relevance": 0.92},
                    {"id": 56, "title": "Sentencia C-005 de 2017", "relevance": 0.78}
                ],
                "confidence_score": 0.89,
                "needs_human_review": False,
                "review_reason": None
            }
        }
    }


class QueryCreate(UserQuery):
    """Esquema para crear nuevas consultas en la base de datos"""
    pass


class QueryUpdate(BaseModel):
    """Esquema para actualizar consultas en la base de datos"""
    status: Optional[QueryStatus] = None
    response_text: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    needs_human_review: Optional[bool] = None
    review_reason: Optional[str] = None
    processed_at: Optional[datetime] = None


class LegalResponse(BaseModel):
    """
    Esquema para respuestas del endpoint de consultas legales directas.
    Este esquema proporciona una respuesta inmediata con referencias legales.
    """
    query: str = Field(..., description="Consulta original del usuario")
    response: str = Field(..., description="Respuesta generada con fundamento legal")
    references: List[Dict[str, Any]] = Field(default=[], description="Referencias a documentos legales utilizados")
    confidence_score: float = Field(..., ge=0, le=1, description="Nivel de confianza en la respuesta (0-1)")
    needs_human_review: bool = Field(default=False, description="Indica si la respuesta requiere revisión por un especialista")
    review_reason: Optional[str] = Field(None, description="Razón por la que se requiere revisión humana")
    processing_time_ms: float = Field(..., description="Tiempo de procesamiento en milisegundos")
    timestamp: str = Field(..., description="Marca de tiempo de la respuesta")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "¿Cuántos días de licencia de maternidad me corresponden?",
                "response": "Según el Código Sustantivo del Trabajo, artículo 236 [Doc1], toda trabajadora en estado de embarazo tiene derecho a una licencia de 18 semanas remuneradas...",
                "references": [
                    {"id": 24, "title": "Código Sustantivo del Trabajo, Artículo 236", "reference": "Art. 236", "relevance": 0.92},
                    {"id": 56, "title": "Sentencia C-005 de 2017", "reference": "SentC-005/2017", "relevance": 0.78}
                ],
                "confidence_score": 0.89,
                "needs_human_review": False,
                "review_reason": None,
                "processing_time_ms": 1250.45,
                "timestamp": "2023-01-01T12:00:05"
            }
        }
    } 