"""
AI Labor Law Assistant - Backend principal
----------------------------------------
Este módulo configura la aplicación FastAPI para el asistente de derecho laboral colombiano.
Incluye rutas API, configuración CORS y conexión a la base de datos.
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api import api_router
from app.db.database import engine, Base

# Cargar variables de entorno
load_dotenv()

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
    allow_origins=["*"],  # Para desarrollo, en producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
