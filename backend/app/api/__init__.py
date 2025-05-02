"""
Paquete de API
-----------
Este paquete contiene las definiciones de rutas y endpoints para la API.
"""

from fastapi import APIRouter
from .endpoints import (
    documents,
    queries,
    search,
    ask,
    search_optimized,
    contrato_realidad,
    indemnizacion,
    contrato,
    documento,
    onboarding,
    escalamiento,
    metricas,
    whatsapp,
    abogado,
    auth,
    facturas,
    casos,
    admin,
    chat,
    notificaciones
)

# Crear un router principal para la API
api_router = APIRouter()

# Incluir los routers de los endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(search_optimized.router, prefix="/search-optimized", tags=["search", "optimized"])
api_router.include_router(ask.router, prefix="/ask", tags=["ask"])
api_router.include_router(contrato_realidad.router, prefix="/contrato-realidad", tags=["contrato-realidad"])
api_router.include_router(indemnizacion.router, prefix="/indemnizacion", tags=["indemnizacion"])
api_router.include_router(contrato.router, prefix="/contrato", tags=["contrato"])
api_router.include_router(documento.router, prefix="/documento", tags=["documento"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(escalamiento.router, prefix="/escalamiento", tags=["escalamiento"])
api_router.include_router(metricas.router, prefix="/metricas", tags=["metricas"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
api_router.include_router(abogado.router, prefix="/abogado", tags=["abogado"])
api_router.include_router(facturas.router, prefix="/facturas", tags=["facturas"])
api_router.include_router(casos.router, prefix="/casos", tags=["casos"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(notificaciones.router, prefix="/notificaciones", tags=["notificaciones"]) 