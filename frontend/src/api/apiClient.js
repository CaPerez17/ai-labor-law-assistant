import axios from 'axios';
import { BACKEND_URL, API_PREFIX } from '../config';

// Mostrar configuración base para debugging
console.log('[BACKEND CONFIG]', { 
  BACKEND_URL, 
  API_PREFIX,
  fullBaseURL: `${BACKEND_URL}${API_PREFIX}`
});

// Alternativas para probar
const URL_ALTERNATIVES = [
  { baseURL: `${BACKEND_URL}${API_PREFIX}`, label: 'Original' },
  { baseURL: `${BACKEND_URL}/api/v1`, label: 'API v1' }, 
  { baseURL: `${BACKEND_URL}`, label: 'Sin prefijo' }
];

// Crear una instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: `${BACKEND_URL}${API_PREFIX}`,
  timeout: 15000, // 15 segundos
  headers: {
    'Content-Type': 'application/json',
  }
});

// Función para probar endpoints alternativos
export const testMetricasEndpoints = async () => {
  console.log('Probando alternativas de endpoint para métricas:');
  
  const results = [];
  const token = localStorage.getItem('token');
  const authHeader = token ? { 'Authorization': `Bearer ${token}` } : {};
  
  for (const alt of URL_ALTERNATIVES) {
    try {
      console.log(`Probando: ${alt.label} - ${alt.baseURL}/metricas/estadisticas`);
      const response = await axios.get(`${alt.baseURL}/metricas/estadisticas`, {
        headers: authHeader,
        timeout: 10000
      });
      console.log(`✅ ${alt.label} funcionó:`, response.status);
      results.push({ 
        label: alt.label, 
        success: true, 
        status: response.status 
      });
    } catch (error) {
      console.error(`❌ ${alt.label} falló:`, {
        status: error.response?.status,
        message: error.message
      });
      results.push({ 
        label: alt.label, 
        success: false, 
        status: error.response?.status,
        message: error.message 
      });
    }
  }
  
  return results;
};

// Interceptor para añadir el token de autenticación a las peticiones
apiClient.interceptors.request.use(
  (config) => {
    // Imprimir la URL de la petición para debugging
    console.log(`[API] Enviando ${config.method.toUpperCase()} a: ${config.baseURL}${config.url}`);
    
    // Añadir token de autenticación si está disponible
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('[API] Error en configuración de petición:', error);
    return Promise.reject(error);
  }
);

// Endpoints específicos de la API - NO incluyen '/api' porque baseURL ya lo tiene
export const endpoints = {
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    refresh: '/auth/refresh',
  },
  user: {
    profile: '/users/me',
    update: '/users/update',
  },
  metricas: {
    estadisticas: '/metricas/estadisticas',
    exportar: '/metricas/exportar',
    registrar: '/metricas/registrar'
  },
  // Otros endpoints que necesites
};

// Función para verificar y loggear la URL completa
const logFullUrl = (endpoint) => {
  const fullUrl = `${BACKEND_URL}${API_PREFIX}${endpoint}`;
  console.log(`[API] URL completa: ${fullUrl}`);
  return fullUrl;
};

// Exportar funciones específicas para diferentes operaciones de API
export const loginUser = async (email, password) => {
  const payload = { username: email, password };
  const body = Object.entries(payload)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');

  console.log('[API] URL completa →', BACKEND_URL + API_PREFIX + endpoints.auth.login);
  console.log('[API] body form-urlencoded →', body);

  const response = await apiClient.post(
    endpoints.auth.login,
    body,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }}
  );

  console.log('Login response status:', response.status);
  console.log('Login response data:', response.data);
  
  const { access_token, user } = response.data;
  return { token: access_token, user };
};

// Exportar el cliente API para su uso en toda la aplicación
export default apiClient; 