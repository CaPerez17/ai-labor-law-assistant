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
  const payload = {
    username: email, // El backend espera username, enviamos el email como username
    password: password
  };
  
  // Log del payload para debugging
  console.log('Payload de login →', payload);
  
  // Log de URL completa para verificar que no hay duplicación de '/api'
  logFullUrl(endpoints.auth.login);
  
  try {
    // Función para convertir un objeto a formato x-www-form-urlencoded
    const formUrlEncoded = (data) => {
      return Object.keys(data)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
        .join('&');
    };
    
    // Primer intento: formato form-urlencoded (estándar OAuth2)
    console.log('[API] Intentando login con formato form-urlencoded (OAuth2 standard)');
    const encodedData = formUrlEncoded(payload);
    console.log('Form data →', encodedData);
    
    const response = await apiClient.post(endpoints.auth.login, 
      encodedData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    
    // Logs para depuración
    console.log('Login response status:', response.status);
    console.log('Login response data:', response.data);
    
    return response;
  } catch (formEncodedError) {
    console.error('[API] Error en login con form-urlencoded:', formEncodedError);
    
    // Si hay una respuesta, mostrar detalles
    if (formEncodedError.response) {
      console.log('Error response status:', formEncodedError.response.status);
      console.log('Error response data:', formEncodedError.response.data);
    }
    
    // Solo intentar con FormData si el error no es 401 (Unauthorized)
    if (formEncodedError.response && formEncodedError.response.status === 401) {
      throw formEncodedError;
    }
    
    // Segundo intento (fallback): formato JSON
    console.log('[API] Intentando login con JSON como fallback');
    try {
      const jsonResponse = await apiClient.post(endpoints.auth.login, payload);
      
      // Logs para depuración
      console.log('JSON Login response status:', jsonResponse.status);
      console.log('JSON Login response data:', jsonResponse.data);
      
      return jsonResponse;
    } catch (jsonError) {
      // Si hay una respuesta, mostrar detalles
      if (jsonError.response) {
        console.log('JSON Error response status:', jsonError.response.status);
        console.log('JSON Error response data:', jsonError.response.data);
      }
      
      // Tercer intento (última opción): formato FormData
      console.log('[API] Intentando login con FormData como último recurso');
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      // Log del formData para debugging
      console.log('FormData de login → username:', email);
      
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
        
        // Si todos los intentos fallan, lanzar el error original
        throw formEncodedError;
      }
    }
  }
};

// Exportar el cliente API para su uso en toda la aplicación
export default apiClient; 