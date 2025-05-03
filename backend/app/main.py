from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL, 
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://legalassista-frontend.onrender.com",
        "https://legalassista.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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