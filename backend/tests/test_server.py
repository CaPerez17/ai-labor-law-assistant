"""
Servidor FastAPI simple para pruebas
----------------------------------
Este script crea un servidor FastAPI mínimo para verificar
que la configuración básica funciona correctamente.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn

# Asegurarnos de que estamos en el directorio correcto
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# Asegurar que el directorio backend esté en sys.path
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importar configuración
import config

# Crear aplicación FastAPI básica
app = FastAPI(title="Servidor de Prueba", description="Servidor para probar la configuración básica")

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "El servidor de prueba está funcionando correctamente",
        "puerto": config.PORT,
        "host": config.HOST,
        "db_url": config.DATABASE_URL,
    }

if __name__ == "__main__":
    print(f"Iniciando servidor de prueba en http://{config.HOST}:{config.PORT}...")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Usar el puerto desde la configuración
    uvicorn.run(app, host=config.HOST, port=config.PORT) 