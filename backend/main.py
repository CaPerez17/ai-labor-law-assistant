"""
AI Labor Law Assistant - Backend principal
----------------------------------------
Este módulo configura la aplicación FastAPI para el asistente de derecho laboral colombiano.
Incluye rutas API, configuración CORS y conexión a la base de datos.
"""

import os
import sys
from pathlib import Path

# Asegurarnos de que el directorio backend esté en sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar configuración centralizada
import config

# Importaciones locales
from app.db.database import engine, Base
from app.api import api_router

# Crear las tablas en la base de datos
# Comentar en producción o si se usa migración
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="AI Labor Law Assistant API",
    description="API para el asistente de derecho laboral colombiano basado en IA",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Configurar el registry antes de importar los routers
registry.configure(
    jwt_secret=settings.JWT_SECRET,
    jwt_algorithm=settings.JWT_ALGORITHM,
    access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    smtp_server=settings.SMTP_SERVER,
    smtp_port=settings.SMTP_PORT,
    smtp_username=settings.SMTP_USERNAME,
    smtp_password=settings.SMTP_PASSWORD,
    smtp_from_email=settings.SMTP_FROM_EMAIL
)
logger.info("Registry inicializado y configurado")
print("🔑 [Registry] Configured with:", registry)

# Importar routers después de configurar el registry
from app.api.endpoints import auth, users, casos, documentos, chat, dashboard

# Incluir los routers de la API
app.include_router(api_router, prefix="/api")

# Ruta raíz para verificar estado del API
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
    
    uvicorn.run(
        "main:app", 
        host=config.HOST, 
        port=config.PORT, 
        reload=config.DEBUG
    )
