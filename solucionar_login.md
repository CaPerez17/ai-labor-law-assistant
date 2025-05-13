# Solución al problema de login en LegalAssista

He identificado y corregido los siguientes problemas:

## Problema 1: URL incorrecta del backend

El frontend estaba intentando conectarse a `https://legalassista-api.onrender.com` pero el backend real está en `https://legalassista.onrender.com`.

**Solución:**
1. Actualicé la configuración en `render.yaml` para reflejar los nombres correctos de los servicios.
2. Actualicé la URL predeterminada en `LoginForm.jsx`.
3. Creé un archivo `.env.production` con la URL correcta del backend.

## Problema 2: Configuración CORS incorrecta

El backend no estaba configurado para aceptar peticiones desde el frontend.

**Solución:**
1. Actualicé la configuración CORS en `main.py` para permitir temporalmente todas las solicitudes (`"*"`) durante las pruebas.
2. Agregué explícitamente el dominio correcto del frontend a la lista de orígenes permitidos.

## Pasos para aplicar la solución en producción:

1. **Actualizar el servicio backend en Render:**
   - Ve a https://dashboard.render.com/
   - Selecciona tu servicio backend
   - En Environment, asegúrate de que `FRONTEND_URL` esté configurado como `https://legalassista-frontend.onrender.com`
   - Haz clic en "Manual Deploy" > "Clear build cache & deploy"

2. **Actualizar el servicio frontend en Render:**
   - Ve al servicio frontend
   - En Environment, asegúrate de que `VITE_BACKEND_URL` esté configurado como `https://legalassista.onrender.com`
   - Haz clic en "Manual Deploy" > "Clear build cache & deploy"

3. **Verifica el inicio de sesión:**
   - Abre https://legalassista-frontend.onrender.com
   - Intenta iniciar sesión con:
     - Email: `admin@legalassista.com`
     - Contraseña: `admin123`
   - Si sigue fallando, abre las herramientas de desarrollo (F12) y verifica:
     - Que la solicitud se está enviando a `https://legalassista.onrender.com/api/auth/login`
     - Que no hay errores CORS en la consola

## Notas adicionales:

1. Los cambios realizados en el repositorio local deberán ser subidos a GitHub para que Render los aplique automáticamente.
2. Si decides mantener el `"*"` en la configuración CORS, esto representa un riesgo de seguridad y debería quitarse una vez que todo funcione correctamente.
3. La estructura correcta del API router es `/api/auth/login` y esta ruta parece estar correctamente configurada en el backend.

Con estos cambios, el sistema de login debería funcionar correctamente permitiendo que usuarios reales se autentiquen en la aplicación. 