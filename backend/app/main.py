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

# Orígenes permitidos para CORS
origins = [
    "https://legalassista-frontend.onrender.com",
    "http://localhost:5173",
    "http://localhost:5174",
    "https://legalassista.onrender.com",
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,  # Caché de preflight por 24 horas
)

# Log para registrar la configuración de CORS
logger.info(f"CORS configurado con orígenes permitidos: {origins}")

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

# Incluir el router de la API
app.include_router(api_router, prefix="/api") 