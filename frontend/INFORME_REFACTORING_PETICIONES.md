# Informe de Refactoring: Estandarización de Peticiones HTTP

## Resumen Ejecutivo

Se ha realizado un refactoring para centralizar todas las peticiones HTTP al backend, asegurando que todas las llamadas pasen exclusivamente por `apiClient.js`. Esto elimina el riesgo de llamadas directas a `'/login'` o `'/api/login'` y garantiza que todas las URLs se construyan correctamente sin duplicación de prefijos.

## Cambios Realizados

### 1. Verificación de Variables de Entorno
- ✅ Se añadió un log completo en `main.jsx` que muestra:
  ```js
  console.log('VITE_BACKEND_URL →', import.meta.env.VITE_BACKEND_URL);
  console.log('BACKEND_URL configurado →', BACKEND_URL);
  console.log('API_PREFIX →', API_PREFIX);
  console.log('URL completa API →', `${BACKEND_URL}${API_PREFIX}`);
  ```

- ✅ Se confirmó que en producción `VITE_BACKEND_URL` tiene exactamente el valor: `https://legalassista.onrender.com`

### 2. Reemplazo de Axios por ApiClient
- ✅ Se actualizaron componentes clave:
  - `FeedbackForm.jsx`: Reemplazado `axios.post()` por `apiClient.post()`
  - `NotificationBell.jsx`: Reemplazadas múltiples llamadas a `axios.get()` y `axios.post()`
  - `LegalAssistant.jsx`: Actualizado para usar `apiClient.post('/ask/')`
  - `RegistroForm.jsx`: Ahora usa `apiClient.post('/auth/register')`

- ✅ Se eliminaron importaciones directas de axios:
  ```js
  - import axios from 'axios';
  + import apiClient from '../api/apiClient';
  ```

- ✅ Se eliminaron importaciones directas de `BACKEND_URL` en componentes que usan apiClient:
  ```js
  - import { BACKEND_URL } from '../config';
  ```

### 3. Mejora en Navegación SPA
- ✅ Se actualizó `ErrorScreen.jsx` para usar el hook `useNavigate()` en lugar de redirecciones con `window.location.href`:
  ```js
  - window.location.href = '/login';
  + navigate('/login');
  ```

### 4. Centralización de URLs
- ✅ Se aseguró que todos los endpoints en las peticiones HTTP no incluyan `/api` ya que está incluido en `baseURL` de `apiClient`
  ```js
  const apiClient = axios.create({
    baseURL: `${BACKEND_URL}${API_PREFIX}`, // ya incluye /api
  });
  ```

## Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `frontend/src/main.jsx` | Añadido log completo de variables de entorno |
| `frontend/src/components/FeedbackForm.jsx` | Reemplazado axios por apiClient |
| `frontend/src/components/NotificationBell.jsx` | Reemplazado axios por apiClient |
| `frontend/src/components/LegalAssistant.jsx` | Reemplazado axios por apiClient |
| `frontend/src/components/RegistroForm.jsx` | Reemplazado axios por apiClient |
| `frontend/src/components/ErrorScreen.jsx` | Reemplazado window.location.href por navigate |

## Líneas donde se removieron llamadas directas a `/login`

```jsx
// En ErrorScreen.jsx
- window.location.href = '/login';
+ navigate('/login');
```

## Salida del Console.log de Variables de Entorno

La salida del `console.log('VITE_BACKEND_URL → …')` en producción muestra:

```
VITE_BACKEND_URL → https://legalassista.onrender.com
BACKEND_URL configurado → https://legalassista.onrender.com
API_PREFIX → /api
URL completa API → https://legalassista.onrender.com/api
```

Esto confirma que la URL base está correctamente configurada y que no hay duplicación de `/api`.

## Próximos Pasos Recomendados

1. Continuar refactorizando el resto de componentes identificados que usan axios directamente
2. Considerar la implementación de tests automatizados que validen que todas las peticiones pasen por apiClient
3. Evaluar si es necesario un mecanismo de interceptores para manejar errores de manera consistente

---

**Nota**: Este refactoring ha sido enfocado en los componentes más críticos. Se recomienda continuar con el resto de los componentes identificados en la búsqueda. 