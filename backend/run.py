"""
Script maestro para iniciar el backend
--------------------------------------
Este script inicia el backend desde cualquier ubicación,
asegurándose de que las rutas y la configuración sean correctas.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Asegurarnos de que estamos en el directorio correcto
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# Asegurar que el directorio backend esté en sys.path
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importar configuración
import config

if __name__ == "__main__":
    print(f"Iniciando servidor en {config.HOST}:{config.PORT}...")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Base de datos: {config.DATABASE_URL}")
    print(f"Debug mode: {config.DEBUG}")
    
    # Iniciar el servidor
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info",
    ) 