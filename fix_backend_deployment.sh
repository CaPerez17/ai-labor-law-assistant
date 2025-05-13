#!/bin/bash

# Script para verificar y corregir el despliegue del backend en Render

echo "Verificando y corregiendo el despliegue del backend en Render"
echo "=========================================================="

echo -e "\nPasos para solucionar el problema:"

echo -e "\n1. Verificar el estado del servicio backend en Render"
echo "   - Ve a https://dashboard.render.com"
echo "   - Haz clic en 'LegalAssista-Backend'"
echo "   - Verifica que el estado sea 'Live' y no haya errores"
echo "   - Revisa los logs para ver errores específicos"

echo -e "\n2. Verificar las variables de entorno en el backend"
echo "   - Asegúrate de que las siguientes variables estén configuradas:"
echo "     * DATABASE_URL (para conectar a PostgreSQL)"
echo "     * CORS_ORIGINS (para permitir peticiones del frontend)"
echo "     * SECRET_KEY (para JWT)"
echo "     * FRONTEND_URL"
echo "   - Estas variables deben estar en la sección 'Environment' del servicio"

echo -e "\n3. Reiniciar el servicio backend"
echo "   - Haz clic en 'Manual Deploy' > 'Clear build cache & deploy'"
echo "   - Esto limpiará la caché y reconstruirá el servicio"

echo -e "\n4. Verificar la configuración en render.yaml"
echo "   - Asegúrate de que el servicio backend esté configurado para exponer la API:"
echo "     ```yaml"
echo "     services:"
echo "       - type: web"
echo "         name: LegalAssista-Backend"
echo "         # Otras configuraciones..."
echo "     ```"

echo -e "\n5. Verificar rutas API definidas en el backend"
echo "   - En el repo, revisa backend/app/main.py para ver cómo se incluyen las rutas"
echo "   - Revisa backend/app/api/api.py para ver los prefijos de las rutas"
echo "   - Ajusta la configuración del frontend según la estructura encontrada"

echo -e "\n6. Configurar variables de entorno en el frontend"
echo "   - Actualiza VITE_BACKEND_URL=https://legalassista-backend.onrender.com"
echo "   - Actualiza VITE_API_PREFIX según corresponda (por ejemplo, /api o /api/v1)"

echo -e "\n7. Probar con un script local para verificar la API"
echo "   - Crea un archivo .env.local en el directorio frontend con:"
echo "     VITE_BACKEND_URL=https://legalassista-backend.onrender.com"
echo "     VITE_API_PREFIX=<prefijo-correcto>"
echo "   - Ejecuta npm run dev para probar localmente"

echo -e "\n8. Activar modo demo (opcional)"
echo "   - Agrega LEGALASSISTA_DEMO=true en el backend para acceso automático"
echo "   - Podrás usar credenciales demo: email_demo@legalassista.com / demo123"

echo -e "\nRecuerda que la solución más probable requiere:"
echo "1. Corregir la configuración del backend para exponer la API correctamente"
echo "2. Actualizar las variables de entorno del frontend para conectar al backend"
echo "3. Desplegar nuevamente ambos servicios con las correcciones"
echo "4. Verificar que ambos servicios estén correctamente configurados para comunicarse entre sí" 