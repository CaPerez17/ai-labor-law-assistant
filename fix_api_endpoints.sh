#!/bin/bash

# Script para identificar y corregir problemas con los endpoints de la API

echo "Identificando problemas con los endpoints de la API"

# URLs de Backend para pruebas
BACKEND_URL="https://legalassista-backend.onrender.com"

# Prueba diferentes rutas para ver cuál funciona
echo "Probando diferentes rutas para encontrar la correcta..."

echo -e "\n1. Probando /api/health"
curl -s "$BACKEND_URL/api/health"

echo -e "\n2. Probando /health"
curl -s "$BACKEND_URL/health"

echo -e "\n3. Probando /api/v1/auth/login"
curl -s -X POST "$BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@legalassista.com","password":"admin123"}'

echo -e "\n4. Probando /api/v1/health"
curl -s "$BACKEND_URL/api/v1/health"

echo -e "\n5. Probando rutas principales"
curl -s "$BACKEND_URL/"
curl -s "$BACKEND_URL/docs"

echo -e "\n6. Verificando ruta de Swagger/OpenAPI"
curl -s "$BACKEND_URL/docs" | grep -o "swagger"

echo -e "\nCon base en estas pruebas, identifica la ruta base correcta de la API."
echo "Si encuentras la ruta, actualiza la configuración del frontend con el prefijo correcto."
echo ""
echo "Solución recomendada:"
echo "1. Ve a la configuración del servicio frontend en Render"
echo "2. Agrega/modifica la variable de entorno VITE_API_PREFIX con el prefijo correcto (por ejemplo, '/api/v1')"
echo "3. Actualiza la variable VITE_BACKEND_URL para que apunte a https://legalassista-backend.onrender.com"
echo "4. Despliega de nuevo el frontend con estos cambios"
echo ""
echo "Alternativamente, puedes verificar el código fuente del backend para confirmar las rutas correctas:"
echo "- Busca en backend/app/main.py cómo se incluyen los routers"
echo "- Busca en backend/app/api/api.py o archivos similares los prefijos de las rutas"
echo "- Verifica el enrutamiento en backend/app/api/endpoints/auth.py para las rutas de autenticación" 