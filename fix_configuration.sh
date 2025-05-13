#!/bin/bash

# Script para solucionar el problema de autenticación entre frontend y backend en Render

echo "Solución al problema de autenticación en LegalAssista"
echo "===================================================="

echo -e "\nProblema detectado:"
echo "1. El frontend está intentando conectarse a https://legalassista-backend.onrender.com/api/auth/login"
echo "2. Pero según render.yaml, el backend está desplegado como https://legalassista-api.onrender.com"
echo "3. Hay un desajuste en los nombres de los servicios"

echo -e "\nSolución:"

echo -e "\n1. Opción 1 - Ajustar el frontend para que use la URL correcta:"
echo "   - En el servicio frontend en Render:"
echo "   - Modifica la variable de entorno VITE_BACKEND_URL=https://legalassista-api.onrender.com"
echo "   - Realiza un nuevo despliegue del frontend"

echo -e "\n2. Opción 2 - Renombrar el servicio backend para que coincida con lo esperado:"
echo "   - En Render, ve al servicio 'legalassista-api'"
echo "   - En la sección 'Settings', cambia el nombre a 'legalassista-backend'"
echo "   - Esto actualizará la URL a https://legalassista-backend.onrender.com"
echo "   - Reinicia el servicio para aplicar los cambios"

echo -e "\n3. Verificar configuración CORS en el backend:"
echo "   - El código muestra que ya tienes https://legalassista-frontend.onrender.com en la lista CORS"
echo "   - Pero asegúrate de que el origen esté correctamente configurado"

echo -e "\nPasos recomendados:"
echo "1. Utiliza la Opción 1 (ajustar el frontend) ya que es menos disruptiva"
echo "2. Edita la variable de entorno VITE_BACKEND_URL en el servicio frontend"
echo "3. Realiza un despliegue manual del frontend"
echo "4. Prueba el inicio de sesión con admin@legalassista.com / admin123"

echo -e "\nDiagnóstico adicional:"
echo "- Según render.yaml, el nombre del servicio backend es 'legalassista-api'"
echo "- En el frontend, se está intentando acceder a 'legalassista-backend'"
echo "- Este desajuste en los nombres de los servicios es la causa del problema"

echo -e "\nSi lo anterior no funciona, activar modo demo:"
echo "1. Agrega LEGALASSISTA_DEMO=true en las variables de entorno del backend"
echo "2. Esto permitirá iniciar sesión con credenciales demo automáticamente"
echo "3. Prueba con cliente_demo@legalassista.com / demo123" 