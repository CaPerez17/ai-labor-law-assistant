/**
 * Configuración central para la aplicación
 * Todas las URLs y valores de configuración deben definirse aquí
 * para garantizar coherencia en toda la aplicación
 */

// Saneamiento definitivo de BACKEND_URL
const raw = import.meta.env.VITE_BACKEND_URL || 'https://legalassista.onrender.com';
// Elimina cualquier sufijo '/api' o '/api/' de raw
export const BACKEND_URL = raw.replace(/\/api\/?$/, '');

// URL para WebSockets
export const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL || 'wss://legalassista.onrender.com/ws';

// Prefijo de API para todas las peticiones
export const API_PREFIX = '/api/v1';

// Registrar las URLs para debugging
console.log('[CONFIG] URLs configuradas:', {
  raw,
  BACKEND_URL,
  WEBSOCKET_URL,
  API_PREFIX,
  ENV: import.meta.env.MODE || 'unknown'
});

// Exportar la configuración como objeto para acceso centralizado
export default {
  BACKEND_URL,
  WEBSOCKET_URL,
  API_PREFIX,
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0'
}; 