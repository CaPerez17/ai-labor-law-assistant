import axios from 'axios';
import { BACKEND_URL, API_PREFIX } from '../config';

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
  // Logs detallados antes de la petición
  console.log('BACKEND_URL final →', BACKEND_URL);
  console.log('API_PREFIX →', API_PREFIX);
  console.log('Endpoint login →', endpoints.auth.login);
  console.log('URL de petición →', BACKEND_URL + API_PREFIX + endpoints.auth.login);
  
  // Crear el payload correcto (username en lugar de email)
  const payload = { username: email, password };
  
  // Log del payload para debugging
  console.log('Payload de login →', payload);
  
  // Log de URL completa para verificar que no hay duplicación de '/api'
  logFullUrl(endpoints.auth.login);
  
  try {
    const body = Object.entries(payload)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join('&');

    console.log('[API] Enviando login como form-urlencoded:', body);

    const response = await apiClient.post(endpoints.auth.login, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    // Logs para depuración
    console.log('Login response status:', response.status);
    console.log('Login response data:', response.data);
    
    return response;
  } catch (error) {
    console.error('[API] Error en login:', error);
    
    // Si hay una respuesta, mostrar detalles
    if (error.response) {
      console.log('Error response status:', error.response.status);
      console.log('Error response data:', error.response.data);
    }
    
    // Propagar el error
    throw error;
  }
};

// Exportar el cliente API para su uso en toda la aplicación
export default apiClient; 