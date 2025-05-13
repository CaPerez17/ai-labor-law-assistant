#!/bin/bash

# Script para verificar y corregir problemas de CORS en el backend

echo "Intentando corregir problemas de CORS para permitir conexiones del frontend"

# URLs relevantes
BACKEND_URL="https://legalassista-backend.onrender.com"
FRONTEND_URL="https://legalassista-frontend.onrender.com"

# Verificar que las URLs sean correctas
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"

# Crear una API temporal para actualizar la configuración CORS del backend
# Esto generalmente requeriría acceso directo al servidor o una API específica
echo "Para corregir el problema de CORS:"
echo "1. Ve al servicio de backend en Render"
echo "2. Agrega o verifica estas variables de entorno:"
echo "   - CORS_ORIGINS=$FRONTEND_URL"
echo "   - FRONTEND_URL=$FRONTEND_URL"
echo "3. Reinicia el servicio de backend para aplicar los cambios"

# Instrucciones para verificar el frontend
echo ""
echo "Para verificar la configuración del frontend:"
echo "1. Ve al servicio de frontend en Render"
echo "2. Verifica que la variable de entorno VITE_BACKEND_URL=$BACKEND_URL"
echo "3. Reinicia el servicio si es necesario"

# Instrucciones para la redirección de API
echo ""
echo "Para verificar la redirección de API:"
echo "1. Abre $FRONTEND_URL/login en el navegador"
echo "2. Abre las herramientas de desarrollador (F12)"
echo "3. Ve a la pestaña 'Network'"
echo "4. Intenta iniciar sesión con admin@legalassista.com / admin123"
echo "5. Verifica que la solicitud de autenticación se dirija a $BACKEND_URL/api/auth/login" 