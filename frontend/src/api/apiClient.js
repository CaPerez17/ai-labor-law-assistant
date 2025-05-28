import axios from 'axios';
import { BACKEND_URL, API_PREFIX } from '../config';

// Registrar URL base final para logging
console.log('[API] URL base configurada:', BACKEND_URL);

// Crear una instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: BACKEND_URL,
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
    login: `${API_PREFIX}/auth/login`,
    register: `${API_PREFIX}/auth/register`,
    refresh: `${API_PREFIX}/auth/refresh`,
  },
  user: {
    profile: `${API_PREFIX}/users/me`,
    update: `${API_PREFIX}/users/update`,
  },
  metricas: {
    estadisticas: `${API_PREFIX}/metricas/estadisticas`,
    exportar: `${API_PREFIX}/metricas/exportar`,
    registrar: `${API_PREFIX}/metricas/registrar`
  },
  // Otros endpoints que necesites
};

// Exportar funciones específicas para diferentes operaciones de API
export const loginUser = async (email, password) => {
  const payload = { username: email, password };
  const body = Object.entries(payload)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');

  try {
    const response = await apiClient.post(
      endpoints.auth.login,
      body,
      { 
        headers: { 
          'Content-Type': 'application/x-www-form-urlencoded' 
        }
      }
    );

    const { access_token, user } = response.data;
    
    if (!access_token || !user) {
      throw new Error('Respuesta de autenticación inválida');
    }
    
    return { token: access_token, user };
  } catch (error) {
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response;
      
      if (status === 401) {
        throw new Error('Usuario o contraseña incorrecta');
      } else if (status === 403) {
        throw new Error('No tiene permisos para acceder');
      } else if (data?.detail) {
        throw new Error(data.detail);
      }
    }
    // Re-lanzar el error original si no es un caso manejado
    throw error;
  }
};

// Exportar el cliente API para su uso en toda la aplicación
export default apiClient;

// Función para obtener analytics/estadísticas
export const getAnalytics = () => apiClient.get(`${API_PREFIX}/metricas/estadisticas`);

// Usuarios (si se usa en UsuariosDashboard)
export const getUsers = () => apiClient.get(`${API_PREFIX}/usuarios`); 