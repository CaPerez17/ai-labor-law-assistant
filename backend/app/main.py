from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.core.config import settings
import logging

# Configuración de logging primero
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Iniciando aplicación LegalAssista")

# Importar y configurar el registry antes de importar los routers
from app.core.registry import registry
# Configurar el registry antes de importar los routers
registry.configure()
logger.info("Registry inicializado y configurado")

# Importar el router de la API después de configurar el registry
from app.api import api_router

# Importar el endpoint temporal de prueba
# NOTA: Eliminar esta importación en producción después de las pruebas
try:
    from backend.add_test_endpoint import add_test_users_endpoint
except ImportError:
    # Intentar con ruta relativa alternativa
    try:
        from add_test_endpoint import add_test_users_endpoint
        # Añadir el endpoint temporal
        add_test_users_endpoint()
        logging.warning("Endpoint temporal /api/auth/test-users añadido (ELIMINAR EN PRODUCCIÓN)")
    except ImportError:
        logging.warning("No se pudo cargar el endpoint de prueba. Esto es normal en producción.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar orígenes para CORS usando variables de entorno
origins = [
    settings.FRONTEND_URL,  # URL del frontend desde config
    "http://localhost:5173",  # Desarrollo local (Vite)
    "http://localhost:5174",  # Desarrollo local alternativo
    "http://localhost:3000",  # Desarrollo local (React)
    "https://legalassista-frontend.onrender.com",  # Frontend en Render
    "https://legalassista.onrender.com",  # Backend en Render (para testing)
]

# Filtrar orígenes vacíos y duplicados
origins = list(set(filter(None, origins)))

# Log detallado de la configuración CORS
logger.info("=== CONFIGURACIÓN CORS ===")
logger.info(f"FRONTEND_URL desde config: {settings.FRONTEND_URL}")
logger.info(f"Orígenes permitidos: {origins}")

# Configurar CORS con configuración completa
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type", 
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Mx-ReqToken",
        "Keep-Alive",
        "X-Requested-With",
        "If-Modified-Since",
    ],
    expose_headers=["*"],
    max_age=86400,  # Caché de preflight por 24 horas
)

logger.info("✅ CORS configurado exitosamente")

# Ruta raíz
@app.get("/")
def read_root():
    return {"status": "online", "message": "LegalAssista API funcionando correctamente"}

# Endpoint health-check
@app.get("/health")
def health():
    return {"status": "ok"}

# Endpoint healthz para Kubernetes
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Endpoint específico para probar CORS
@app.get("/cors-test")
def cors_test(request: Request):
    """Endpoint específico para probar la configuración de CORS"""
    origin = request.headers.get("origin", "No origin header")
    return {
        "status": "ok",
        "message": "CORS funcionando correctamente",
        "origin": origin,
        "allowed_origins": origins,
        "cors_configured": True
    }

# Incluir el router de la API
app.include_router(api_router, prefix=settings.API_V1_STR) 