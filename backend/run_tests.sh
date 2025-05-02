#!/bin/bash

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar dependencias de prueba si no están instaladas
pip install pytest pytest-asyncio httpx

# Configurar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Ejecutar las pruebas
pytest app/tests/ -v 