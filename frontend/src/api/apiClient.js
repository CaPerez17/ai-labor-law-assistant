import axios from 'axios';
import { BACKEND_URL, API_PREFIX } from '../config';

// Registrar URL base final para logging
console.log('[API] URL base configurada:', `${BACKEND_URL}${API_PREFIX}`);

// Crear una instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: `${BACKEND_URL}${API_PREFIX}`,
  timeout: 15000, // 15 segundos
  headers: {
    'Content-Type': 'application/json',
  }
});

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

// Endpoints específicos de la API - NO incluyen '/api/v1' porque baseURL ya lo tiene
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

// Exportar funciones específicas para diferentes operaciones de API
export const loginUser = async (email, password) => {
  const payload = { username: email, password };
  const body = Object.entries(payload)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');

  console.log('[API] URL login:', `${BACKEND_URL}${API_PREFIX}${endpoints.auth.login}`);

  const response = await apiClient.post(
    endpoints.auth.login,
    body,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }}
  );
  
  const { access_token, user } = response.data;
  return { token: access_token, user };
};

// Exportar el cliente API para su uso en toda la aplicación
export default apiClient;

// Función para obtener analytics/estadísticas
export const getAnalytics = () => apiClient.get('/metricas/estadisticas'); 