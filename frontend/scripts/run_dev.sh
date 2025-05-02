#!/bin/bash

# Instalar dependencias
echo "Instalando dependencias del frontend..."
npm install

# Configurar variables de entorno si no existen
if [ ! -f ".env" ]; then
    echo "Creando archivo .env desde el ejemplo"
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env
        echo "NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws" >> .env
    fi
fi

# Iniciar el servidor de desarrollo
echo "Iniciando servidor de desarrollo Next.js..."
npm run dev 