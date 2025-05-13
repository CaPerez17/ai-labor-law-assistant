# Solución forzada para problema de URL del backend en LegalAssista

Este documento describe la solución implementada para forzar la URL correcta del backend en el frontend de LegalAssista. Esta solución fue necesaria debido a problemas persistentes donde el frontend intentaba conectarse a `https://legalassista-api.onrender.com` en lugar de `https://legalassista.onrender.com`.

## 📋 Resumen del problema

- El frontend intentaba conectarse a: `https://legalassista-api.onrender.com`
- La URL correcta del backend es: `https://legalassista.onrender.com`
- A pesar de tener la configuración correcta en `.env.production` y `config.js`, el problema persistía
- Error común: `404 Not Found` y problemas de CORS al intentar iniciar sesión

## 🔧 Solución implementada

Se implementó una solución de emergencia que fuerza la URL correcta a varios niveles:

### 1. Script en `index.html`

Se añadió un script al inicio del archivo HTML para definir las variables globales:

```html
<script>
  // Forzar la URL correcta del backend
  window.CORRECT_BACKEND_URL = 'https://legalassista.onrender.com';
  window.CORRECT_WEBSOCKET_URL = 'wss://legalassista.onrender.com/ws';
  
  // Asegurarse de que las variables de entorno sean correctas
  window.VITE_BACKEND_URL = window.CORRECT_BACKEND_URL;
  window.VITE_WEBSOCKET_URL = window.CORRECT_WEBSOCKET_URL;
  
  console.log('[EMERGENCY CONFIG] Forzando URL del backend:', window.CORRECT_BACKEND_URL);
</script>
```

### 2. Archivo `config_override.js`

Se creó un archivo especial que sobreescribe las variables de entorno en tiempo de ejecución:

```javascript
// Forzar la URL correcta del backend
const CORRECT_BACKEND_URL = 'https://legalassista.onrender.com';

// Sobreescribir la variable de entorno en runtime
if (window) {
  window.VITE_BACKEND_URL = CORRECT_BACKEND_URL;
  window.VITE_WEBSOCKET_URL = 'wss://legalassista.onrender.com/ws';
}

// Sobreescribir también import.meta.env si es accesible
try {
  if (import.meta && import.meta.env) {
    import.meta.env.VITE_BACKEND_URL = CORRECT_BACKEND_URL;
  }
} catch (error) {
  console.warn('[CONFIG_OVERRIDE] Error:', error.message);
}
```

### 3. Importación temprana en `main.jsx` y `App.jsx`

Se modificaron los archivos principales para importar la configuración de emergencia lo antes posible:

```javascript
// En main.jsx
import './config_override.js';
```

```javascript
// En App.jsx
import './config_override';
import { BACKEND_URL } from './config';

// Verificar en useEffect
useEffect(() => {
  console.log('[App] URL del backend configurada:', BACKEND_URL);
  if (window.forceCorrectBackendURL) {
    window.forceCorrectBackendURL();
  }
}, []);
```

### 4. Script de verificación de configuración

Se creó un script para verificar que todas las configuraciones sean correctas:

```bash
npm run check-config
```

Este script verifica:
- El contenido de `.env.production`
- El archivo `config.js`
- El archivo `index.html`

## 🚀 Instrucciones para desplegar la solución

1. Asegúrate de que todos los archivos modificados estén incluidos en tu build:
   - `frontend/index.html`
   - `frontend/src/config_override.js`
   - `frontend/src/main.jsx`
   - `frontend/src/App.jsx`

2. Ejecuta la verificación de configuración:
   ```bash
   cd frontend
   npm run check-config
   ```

3. Construye y despliega el frontend:
   ```bash
   npm run build
   # Desplegar en Render.com
   ```

4. Después del despliegue, verifica manualmente:
   - Abre la consola del navegador al cargar la aplicación
   - Observa los mensajes con prefijo `[EMERGENCY CONFIG]` y `[CONFIG_OVERRIDE]`
   - Confirma que la URL mostrada sea `https://legalassista.onrender.com`

5. Intenta iniciar sesión con credenciales válidas:
   - admin@legalassista.com / admin123
   - abogado@legalassista.com / abogado123
   - cliente@legalassista.com / cliente123

## ⚠️ Consideraciones

Esta es una solución de emergencia para resolver un problema persistente. Una vez que el login funcione correctamente en producción, se recomienda:

1. Investigar la causa raíz del problema (posiblemente caché persistente o error de configuración en Render.com)
2. Considerar una solución más limpia una vez identificada la causa
3. Mantener el script de verificación de configuración como parte del proceso de build

## 🧪 Depuración adicional

Si persisten los problemas después de esta solución, se recomienda:

1. Usar el panel de depuración en el formulario de login (botón "Mostrar información técnica")
2. Ejecutar la función de prueba de login desde la consola del navegador:
   ```javascript
   testLogin('admin@legalassista.com', 'admin123')
   ```
3. Revisar los logs del backend en Render.com para verificar si las solicitudes están llegando
4. Considerar un redesplegue completo del backend y frontend

---

Documentación preparada para el equipo de desarrollo de LegalAssista
Fecha: [Fecha actual] 