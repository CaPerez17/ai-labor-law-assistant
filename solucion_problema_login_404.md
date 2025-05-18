# Solución al problema 404 en la petición de login

## 🔍 Diagnóstico del problema

Se detectó un error crítico en producción donde la petición de login estaba fallando con un código 404, debido a que la URL de petición estaba construida incorrectamente:

- **URL incorrecta**: `https://legalassista.onrender.com/login`
- **URL correcta**: `https://legalassista.onrender.com/api/auth/login`

La causa principal era que no existía una configuración centralizada para gestionar las URLs de API, lo que provocaba:

1. **Inconsistencia en la construcción de URLs**: Algunas peticiones incluían el prefijo `/api/` manualmente, mientras otras no.
2. **Hardcoding de URLs**: Las URLs estaban escritas directamente en múltiples componentes, dificultando el mantenimiento.
3. **Falta de configuración por entorno**: No existía gestión adecuada de variables de entorno para desarrollo vs. producción.

## ✅ Solución implementada

La solución se ha implementado a través de varios cambios clave:

### 1. Cliente API centralizado

Se creó un módulo dedicado `apiClient.js` que configura Axios de manera centralizada:

```javascript
import axios from 'axios';
import { BACKEND_URL, API_PREFIX } from '../config';

const apiClient = axios.create({
  baseURL: `${BACKEND_URL}${API_PREFIX}`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// ... resto del archivo
```

Este cliente API:
- Configura `baseURL` correctamente combinando la URL base del backend y el prefijo de API
- Añade interceptores para logging y gestión de tokens de autenticación
- Exporta endpoints y funciones específicas como `loginUser()`

### 2. Mejora en la configuración de variables

Se refactorizó `config.js` para usar variables de entorno con fallbacks:

```javascript
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://legalassista.onrender.com';
export const API_PREFIX = '/api';
```

Además, se crearon archivos de entorno separados:
- `.env.production`: Variables para el entorno de producción
- `.env.development`: Variables para el entorno de desarrollo

### 3. Refactorización del componente LoginForm

Se reemplazó la llamada directa a axios por la función centralizada:

```javascript
// Antes:
response = await axios.post(`${BACKEND_URL}/api/auth/login`, {...

// Después:
const response = await loginUser(email, password);
```

Esto garantiza consistencia en las llamadas API y mejora la mantenibilidad del código.

## 📊 Ventajas del nuevo enfoque

1. **Consistencia**: Todas las URLs se construyen de manera uniforme.
2. **Mantenibilidad**: Si cambia la URL base o el prefijo de API, solo hay que modificarlo en un lugar.
3. **Debugging mejorado**: Se añadieron logs detallados para facilitar la depuración.
4. **Mayor robustez**: Se implementó manejo de errores específicos para diferentes escenarios.
5. **Soporte para entornos**: La configuración se adapta automáticamente a desarrollo o producción.

## 🔄 Pasos para verificar

1. **Desarrollo local**: Usar el entorno de desarrollo con variables locales.
2. **Producción**: Verificar que la URL correcta se está utilizando al desplegar.

Para testear la URL en la consola del navegador:

```javascript
// Verificar URL base
console.log(apiClient.defaults.baseURL);

// Verificar URL completa del login
console.log(apiClient.defaults.baseURL + '/auth/login');
```

## 🛡️ Prevención de errores similares

Para evitar problemas similares en el futuro:

1. **Nunca construir URLs manualmente** en los componentes.
2. **Siempre usar el cliente API centralizado** para todas las peticiones.
3. **Revisar logs** antes de desplegar a producción.
4. **Añadir test unitarios** que verifiquen la construcción correcta de URLs. 