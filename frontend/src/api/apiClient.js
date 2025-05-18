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
  // Log de URL completa para verificar que no hay duplicación de '/api'
  logFullUrl(endpoints.auth.login);
  
  try {
    // Primer intento: formato JSON
    const response = await apiClient.post(endpoints.auth.login, { email, password });
    
    // Logs para depuración
    console.log('Login response status:', response.status);
    console.log('Login response data:', response.data);
    
    return response;
  } catch (jsonError) {
    console.error('[API] Error en login con JSON:', jsonError);
    
    // Si hay una respuesta, mostrar detalles
    if (jsonError.response) {
      console.log('Error response status:', jsonError.response.status);
      console.log('Error response data:', jsonError.response.data);
    }
    
    // Solo intentar con FormData si el error no es 401 (Unauthorized)
    if (jsonError.response && jsonError.response.status === 401) {
      throw jsonError;
    }
    
    // Segundo intento: formato FormData (para compatibilidad con OAuth2)
    console.log('[API] Intentando login con FormData');
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    // Crear una instancia separada para FormData
    const formDataConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };
    
    try {
      // Log de URL completa antes de hacer petición con FormData
      logFullUrl(endpoints.auth.login);
      
      const formDataResponse = await apiClient.post(endpoints.auth.login, formData, formDataConfig);
      
      // Logs para depuración
      console.log('FormData Login response status:', formDataResponse.status);
      console.log('FormData Login response data:', formDataResponse.data);
      
      return formDataResponse;
    } catch (formDataError) {
      // Si hay una respuesta, mostrar detalles
      if (formDataError.response) {
        console.log('FormData Error response status:', formDataError.response.status);
        console.log('FormData Error response data:', formDataError.response.data);
      }
      
      throw formDataError;
    }
  }
};

// Exportar el cliente API para su uso en toda la aplicación
export default apiClient; 