import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// Importar el cliente de API y la función login en lugar de axios directo
import { loginUser } from '../api/apiClient';
import { BACKEND_URL } from '../config';

const LoginForm = (props) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showDebug, setShowDebug] = useState(false);
    const navigate = useNavigate();

    // Mostrar la URL del backend al cargar el componente
    useEffect(() => {
        console.log(`[LoginForm] URL de backend configurada: ${BACKEND_URL}`);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Limpiar errores anteriores
        setError('');
        setLoading(true);
        
        console.log(`[LoginForm] Iniciando proceso de login...`);

        try {
            // Utilizar la función loginUser que encapsula la lógica de login
            const response = await loginUser(email, password);
            
            console.log('[LoginForm] Login exitoso, respuesta:', response.data);
            
            // Verificar el status de la respuesta
            if (response.status !== 200) {
                console.error('[LoginForm] La respuesta no tiene status 200:', response.status);
                throw new Error(`Error de autenticación: ${response.data.message || 'Respuesta del servidor inválida'}`);
            }
            
            // Si llegamos aquí, el login fue exitoso
            if (!response || !response.data) {
                throw new Error('La respuesta del servidor está vacía');
            }
            
            // Verificar estructura de la respuesta
            const accessToken = response.data.access_token || response.data.token;
            if (!accessToken) {
                console.error('[LoginForm] Respuesta sin token:', response.data);
                throw new Error('La respuesta no contiene un token de acceso');
            }
            
            // Almacenar el token
            localStorage.setItem('token', accessToken);
            console.log('[LoginForm] Token guardado en localStorage');
            
            // Verificar datos de usuario
            if (!response.data.user) {
                console.error('[LoginForm] Respuesta sin datos de usuario:', response.data);
                throw new Error('La respuesta no contiene datos de usuario');
            }
            
            // Almacenar datos de usuario
            localStorage.setItem('user', JSON.stringify(response.data.user));
            console.log('[LoginForm] Datos de usuario guardados en localStorage:', response.data.user);
            
            // Redirigir según el rol
            const userRole = response.data.user.rol || response.data.user.role;
            
            if (!userRole) {
                console.error('[LoginForm] Usuario sin rol definido:', response.data.user);
                throw new Error('El usuario no tiene un rol definido');
            }
            
            console.log(`[LoginForm] Rol del usuario: ${userRole}`);
            
            // Desactivar estado de carga
            setLoading(false);
            
            // Pasar los datos de usuario al componente App a través de la función onLoginSuccess
            // IMPORTANTE: Esto debe ser ANTES de navegar para evitar pérdida de estado
            if (props.onLoginSuccess) {
                console.log('[LoginForm] Ejecutando onLoginSuccess con datos de usuario:', response.data.user);
                props.onLoginSuccess(response.data.user);
                
                // Dar tiempo para que el estado se actualice antes de navegar
                console.log('[LoginForm] Esperando antes de navegar...');
                
                setTimeout(() => {
                    console.log('[LoginForm] Navegando a dashboard basado en rol:', userRole.toLowerCase());
                    if (userRole.toLowerCase() === 'admin') {
                        navigate('/admin/metricas');
                    } else if (userRole.toLowerCase() === 'abogado' || userRole.toLowerCase() === 'lawyer') {
                        navigate('/abogado');
                    } else {
                        navigate('/cliente');
                    }
                }, 500); // Aumentar el timeout para asegurar que el estado se actualiza
            } else {
                console.warn('[LoginForm] ¡ADVERTENCIA! props.onLoginSuccess no está definido');
                console.log('[LoginForm] Estado actual de props:', props);
                
                // Fallback para navegar si no hay onLoginSuccess
                setTimeout(() => {
                    console.log('[LoginForm] Navegando a dashboard (sin onLoginSuccess) basado en rol:', userRole.toLowerCase());
                    if (userRole.toLowerCase() === 'admin') {
                        navigate('/admin/metricas');
                    } else if (userRole.toLowerCase() === 'abogado' || userRole.toLowerCase() === 'lawyer') {
                        navigate('/abogado');
                    } else {
                        navigate('/cliente');
                    }
                }, 500);
            }
            
        } catch (err) {
            console.error('[LoginForm] Error en el proceso de login:', err);
            
            // Garantizar que loading se desactiva
            setLoading(false);
            
            // Manejar diferentes tipos de errores
            if (err.response) {
                // El servidor respondió con un código de estado diferente de 2xx
                const statusCode = err.response.status;
                
                if (statusCode === 401) {
                    setError('Credenciales incorrectas. Por favor verifica tu email y contraseña.');
                } else if (statusCode === 404) {
                    setError(`El servicio de autenticación no está disponible (404). Verifica la URL de la API.`);
                } else if (statusCode === 500) {
                    setError('Error interno del servidor. Por favor intenta más tarde.');
                } else {
                    const errorMsg = err.response.data?.detail || err.response.data?.message || 'Error desconocido';
                    setError(`Error HTTP ${statusCode}: ${errorMsg}`);
                }
                
                // Log para depuración
                console.error('Detalles de respuesta:', {
                    status: err.response.status,
                    headers: err.response.headers,
                    data: err.response.data
                });
            } else if (err.request) {
                // La solicitud fue hecha pero no se recibió respuesta
                if (err.code === 'ECONNABORTED') {
                    setError('La solicitud ha excedido el tiempo de espera. El servidor puede estar sobrecargado.');
                } else {
                    setError(`No se pudo contactar al servidor. Verifica tu conexión a internet y que la URL del backend sea correcta.`);
                }
            } else {
                // Error al configurar la solicitud
                setError(`Error en la solicitud: ${err.message || 'Error desconocido'}`);
            }
            
            return; // Salir de la función
        } finally {
            // Garantizar que el estado de carga se desactiva
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-md">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Iniciar Sesión en LegalAssista
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Tu asistente legal inteligente
                    </p>
                </div>
                
                {error && (
                    <div className="bg-red-50 border-l-4 border-red-400 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                    </div>
                )}
                
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="email-address" className="sr-only">Correo electrónico</label>
                            <input
                                id="email-address"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Correo electrónico"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                disabled={loading}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">Contraseña</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Contraseña"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-70"
                        >
                            {loading ? (
                                <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                                    <svg className="animate-spin h-5 w-5 text-indigo-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                </span>
                            ) : (
                                <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                                    <svg className="h-5 w-5 text-indigo-500 group-hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                        <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                                    </svg>
                                </span>
                            )}
                            {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
                        </button>
                    </div>
                </form>

                {/* Panel de depuración condicional */}
                <div className="mt-6 text-center">
                    <button 
                        onClick={() => setShowDebug(!showDebug)} 
                        className="text-sm text-gray-500 hover:text-gray-700"
                        disabled={loading}
                    >
                        {showDebug ? 'Ocultar información técnica' : 'Mostrar información técnica'}
                    </button>
                </div>

                {showDebug && (
                    <div className="mt-4 p-4 border rounded-md bg-gray-50">
                        <h3 className="text-sm font-medium text-gray-800">Información de depuración:</h3>
                        <p className="text-xs mt-1">Backend URL: {BACKEND_URL}</p>
                        <p className="text-xs mt-1">API Base URL: {`${BACKEND_URL}/api`}</p>
                        <p className="text-xs mt-1">Endpoint Login: <code>/auth/login</code></p>
                        <p className="text-xs mt-1">URL completa: <code>{`${BACKEND_URL}/api/auth/login`}</code></p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoginForm; 