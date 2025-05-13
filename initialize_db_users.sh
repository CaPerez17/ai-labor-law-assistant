#!/bin/bash

# Script para inicializar usuarios en la base de datos
echo "Ejecutando script de inicialización de usuarios..."

# Verificar si estamos en el directorio correcto
if [ ! -d "backend" ]; then
    echo "Error: Este script debe ejecutarse desde el directorio raíz del proyecto donde está la carpeta 'backend'."
    exit 1
fi

# Ejecutar el script seed.py
cd backend
python scripts/seed.py

echo ""
echo "Para verificar los usuarios creados, conecte a la base de datos y ejecute:"
echo "  SELECT email, rol, activo FROM usuarios;" 