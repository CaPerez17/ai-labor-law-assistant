/**
 * CONFIGURACIÓN DE EMERGENCIA
 * --------------------------
 * Este archivo fuerza la URL correcta del backend independientemente 
 * de la configuración en .env y está diseñado para solucionar problemas
 * persistentes con la URL del backend.
 * 
 * IMPORTANTE: Este archivo debe ser importado en index.html o en App.jsx
 * para garantizar que se ejecute antes de cualquier solicitud al backend.
 */

// Forzar la URL correcta del backend
const CORRECT_BACKEND_URL = 'https://legalassista.onrender.com';

// Sobreescribir la variable de entorno en runtime
if (window && window.Vite) {
  window.Vite = {
    ...window.Vite,
    env: {
      ...window.Vite.env,
      VITE_BACKEND_URL: CORRECT_BACKEND_URL,
      VITE_WEBSOCKET_URL: 'wss://legalassista.onrender.com/ws'
    }
  };
} else if (window) {
  // Si no existe window.Vite, crear un objeto global
  window.VITE_BACKEND_URL = CORRECT_BACKEND_URL;
  window.VITE_WEBSOCKET_URL = 'wss://legalassista.onrender.com/ws';
}

// Sobreescribir también import.meta.env si es accesible
try {
  if (import.meta && import.meta.env) {
    import.meta.env = {
      ...import.meta.env,
      VITE_BACKEND_URL: CORRECT_BACKEND_URL,
      VITE_WEBSOCKET_URL: 'wss://legalassista.onrender.com/ws'
    };
  }
} catch (error) {
  console.warn('[CONFIG_OVERRIDE] No se pudo acceder a import.meta.env:', error.message);
}

// Ejecutar un console.log para confirmar que el archivo se está cargando
console.log('[CONFIG_OVERRIDE] Configuración forzada:', {
  BACKEND_URL: CORRECT_BACKEND_URL,
  WEBSOCKET_URL: 'wss://legalassista.onrender.com/ws'
});

// Exponer la función para verificar y forzar la configuración en cualquier momento
window.forceCorrectBackendURL = function() {
  // Verificar si config.js está usando la URL correcta
  const currentConfig = window.BACKEND_URL || (import.meta && import.meta.env ? import.meta.env.VITE_BACKEND_URL : null);
  
  console.log('[CONFIG_OVERRIDE] URL actual del backend:', currentConfig);
  
  if (currentConfig && currentConfig !== CORRECT_BACKEND_URL) {
    console.warn(`[CONFIG_OVERRIDE] URL incorrecta detectada: ${currentConfig}`);
    console.warn(`[CONFIG_OVERRIDE] Forzando URL correcta: ${CORRECT_BACKEND_URL}`);
    
    // Sobreescribir
    window.BACKEND_URL = CORRECT_BACKEND_URL;
    
    try {
      if (import.meta && import.meta.env) {
        import.meta.env.VITE_BACKEND_URL = CORRECT_BACKEND_URL;
      }
    } catch (error) {
      console.warn('[CONFIG_OVERRIDE] Error al actualizar import.meta.env:', error.message);
    }
    
    return true;
  }
  
  console.log('[CONFIG_OVERRIDE] La URL del backend ya es correcta:', currentConfig);
  return false;
};

// Exportar por si se necesita importar como módulo
export const BACKEND_URL = CORRECT_BACKEND_URL;
export const WEBSOCKET_URL = 'wss://legalassista.onrender.com/ws';

export default {
  BACKEND_URL,
  WEBSOCKET_URL,
  forceCorrectURL: window.forceCorrectBackendURL
}; 