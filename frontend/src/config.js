/**
 * Configuración central para la aplicación
 * Todas las URLs y valores de configuración deben definirse aquí
 * para garantizar coherencia en toda la aplicación
 */

// URL del backend para las peticiones a la API
export const BACKEND_URL = 'https://legalassista.onrender.com';

// URL para WebSockets
export const WEBSOCKET_URL = 'wss://legalassista.onrender.com/ws';

// Función para debugging de las URLs
export const logApiCall = (endpoint) => {
  console.log(`[API] Llamando a: ${BACKEND_URL}${endpoint}`);
  return `${BACKEND_URL}${endpoint}`;
};

// Exportar la configuración como objeto para acceso centralizado
export default {
  BACKEND_URL,
  WEBSOCKET_URL,
  API_PREFIX: '/api',
  logApiCall
}; 