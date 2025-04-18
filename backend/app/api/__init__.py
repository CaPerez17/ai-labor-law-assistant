"""
Paquete de API
-----------
Este paquete contiene las definiciones de rutas y endpoints para la API.
"""

from fastapi import APIRouter
from .endpoints import documents, queries, search, ask, search_optimized

# Crear un router principal para la API
api_router = APIRouter()

# Incluir los routers de los endpoints
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(search_optimized.router, prefix="/search-optimized", tags=["search", "optimized"])
api_router.include_router(ask.router, prefix="/ask", tags=["ask"]) 