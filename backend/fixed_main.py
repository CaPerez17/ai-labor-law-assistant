"""
AI Labor Law Assistant - Backend principal (versión corregida)
-----------------------------------------------------------
Versión corregida del archivo main.py con las importaciones adecuadas
y la configuración correcta de CORS para permitir el acceso desde Render.
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurarnos de que el directorio backend esté en sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar configuración y modelos
from app.core.config import settings
from app.db.database import engine, Base
from app.api.api import api_router

# Importar módulos del registry y auth
from app.core.security import get_password_hash
from app.core import security

# Crear las tablas en la base de datos (comentar en producción o usar migraciones)
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="AI Labor Law Assistant API",
    description="API para el asistente de derecho laboral colombiano basado en IA",
    version="0.1.0",
    openapi_url="/api/openapi.json",
)

# Configurar CORS - Incluir el dominio de Render
origins = [
    "http://localhost:5173", 
    "http://localhost:3000", 
    "http://127.0.0.1:5173", 
    "http://127.0.0.1:3000", 
    "http://localhost:5174", 
    "http://127.0.0.1:5174",
    "https://legalassista-frontend.onrender.com",  # Frontend en Render
]

# Añadir middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Incluir los routers de API
app.include_router(api_router, prefix="/api")

# Ruta para verificar estado del API
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "AI Labor Law Assistant API está funcionando correctamente",
        "version": "0.1.0",
    }

# Ruta para verificar estado de salud
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Punto de entrada para ejecutar con uvicorn
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Iniciando servidor en {host}:{port}")
    uvicorn.run(
        "fixed_main:app", 
        host=host,
        port=port,
        reload=settings.DEBUG
    ) 