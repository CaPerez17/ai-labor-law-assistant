#!/bin/bash

# Configuración de variables de entorno
export PORT=${PORT:-8000}
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Verificación de variables críticas
echo "Verificando variables de entorno..."
if [ -z "$OPENAI_API_KEY" ]; then
  echo "⚠️ ADVERTENCIA: OPENAI_API_KEY no está configurada"
fi

if [ -z "$DATABASE_URL" ]; then
  echo "⚠️ ADVERTENCIA: DATABASE_URL no está configurada, usando SQLite local"
fi

echo "🚀 Iniciando LegalAssista API en puerto $PORT"

# Iniciar la aplicación
cd app
exec uvicorn main:app --host 0.0.0.0 --port $PORT 