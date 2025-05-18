/**
 * Configuración central para la aplicación
 * Todas las URLs y valores de configuración deben definirse aquí
 * para garantizar coherencia en toda la aplicación
 */

// URL del backend para las peticiones a la API
// Intentar usar variable de entorno primero, luego URL fija
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://legalassista.onrender.com';

// URL para WebSockets
export const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL || 'wss://legalassista.onrender.com/ws';

// Prefijo de API para todas las peticiones
export const API_PREFIX = '/api';

// Registrar las URLs para debugging
console.log('[CONFIG] URLs configuradas:', {
  BACKEND_URL,
  WEBSOCKET_URL,
  API_PREFIX,
  ENV: import.meta.env.MODE || 'unknown'
});

// Función para debugging de las URLs
export const logApiCall = (endpoint) => {
  const url = `${BACKEND_URL}${API_PREFIX}${endpoint}`;
  console.log(`[API] Llamando a: ${url}`);
  return url;
};

// Exportar la configuración como objeto para acceso centralizado
export default {
  BACKEND_URL,
  WEBSOCKET_URL,
  API_PREFIX,
  logApiCall,
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0'
}; 