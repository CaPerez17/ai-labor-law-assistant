#!/bin/bash

# Script para verificar la configuración del frontend

echo "Verificando la configuración del frontend en Render"

# Obtener la variable de entorno actual del frontend
echo "Para verificar que el frontend esté conectando correctamente con el backend:"
echo ""
echo "1. Verifica estas variables de entorno en el servicio frontend en Render:"
echo "   - VITE_BACKEND_URL=https://legalassista-backend.onrender.com"
echo ""
echo "2. Crea un archivo temporal .env.production en la raíz del proyecto frontend con:"
echo "VITE_BACKEND_URL=https://legalassista-backend.onrender.com"
echo ""
echo "3. Realiza un despliegue manual del frontend para aplicar los cambios"
echo ""
echo "4. Para verificar las peticiones de red desde el navegador:"
echo "   a. Abre https://legalassista-frontend.onrender.com"
echo "   b. Abre las herramientas de desarrollo (F12)"
echo "   c. Ve a la pestaña 'Network'"
echo "   d. Intenta iniciar sesión y verifica que las URLs contengan:"
echo "      https://legalassista-backend.onrender.com/api/auth/login"

# Instrucciones para depurar modo demo
echo ""
echo "Si quieres activar el modo demo para pruebas:"
echo "1. Agrega esta variable de entorno al backend en Render:"
echo "   - LEGALASSISTA_DEMO=true"
echo "2. Reinicia el servicio backend"
echo "3. Intenta iniciar sesión con:"
echo "   - admin_demo@legalassista.com / demo123"
echo "   - cliente_demo@legalassista.com / demo123"
echo "   - abogado_demo@legalassista.com / demo123" 