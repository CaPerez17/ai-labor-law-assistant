/**
 * CONFIGURACIÓN FIJA PARA LEGALASSISTA
 * --------------------------
 * Este archivo define URLs fijas para acceder al backend
 * independientemente de variables de entorno.
 */

// URLs fijas para la aplicación
export const BACKEND_URL = 'https://legalassista.onrender.com';
export const WEBSOCKET_URL = 'wss://legalassista.onrender.com/ws';

// Registrar las URLs para debugging
console.log('[CONFIG] Usando URLs fijas:', {
  BACKEND_URL,
  WEBSOCKET_URL
});

// Función simple para registro de llamadas API
export const logApiCall = (endpoint) => {
  console.log(`[API] Llamando a: ${BACKEND_URL}${endpoint}`);
  return `${BACKEND_URL}${endpoint}`;
};

// Exportar configuración como objeto
export default {
  BACKEND_URL,
  WEBSOCKET_URL,
  API_PREFIX: '/api',
  logApiCall
}; 