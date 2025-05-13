import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { BACKEND_URL } from '../config_override';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [backendUrl, setBackendUrl] = useState(BACKEND_URL);
    const [showDebug, setShowDebug] = useState(false);
    const navigate = useNavigate();

    // Mostrar la URL del backend al cargar el componente
    useEffect(() => {
        console.log(`[LoginForm] URL de backend configurada: ${BACKEND_URL}`);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            console.log(`Intentando login en: ${BACKEND_URL}/api/auth/login`);
            
            // Intentar primero con formato JSON
            try {
                const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
                    email: email,
                    password: password
                }, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log("Login exitoso con formato JSON");
                
                // Verificar si tenemos un token de acceso
                if (response.data && response.data.access_token) {
                    // Almacenar el token
                    localStorage.setItem('token', response.data.access_token);
                    
                    // Verificar que user existe antes de almacenarlo
                    if (response.data.user) {
                        localStorage.setItem('user', JSON.stringify(response.data.user));
                        
                        // Redirigir según el rol del usuario
                        const userRole = response.data.user.role;
                        if (userRole === 'admin') {
                            navigate('/admin');
                        } else if (userRole === 'lawyer') {
                            navigate('/abogado');
                        } else {
                            navigate('/cliente');
                        }
                    } else {
                        console.error("La respuesta no contiene datos de usuario");
                        setError("Error: La respuesta del servidor no incluye datos de usuario");
                    }
                } else {
                    console.error("La respuesta no contiene token de acceso");
                    setError("Error: La respuesta del servidor no incluye token de acceso");
                }
                return;
            } catch (jsonError) {
                console.error("Error con formato JSON, intentando con FormData:", jsonError);
                // Si falla, intentamos con FormData como respaldo
            }
            
            // Intentar con FormData (formato que espera OAuth2)
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);
            
            const response = await axios.post(`${BACKEND_URL}/api/auth/login`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            
            console.log("Login exitoso con FormData");
            
            // Verificar si tenemos un token de acceso
            if (response.data && response.data.access_token) {
                // Almacenar el token
                localStorage.setItem('token', response.data.access_token);
                
                // Verificar que user existe antes de almacenarlo
                if (response.data.user) {
                    localStorage.setItem('user', JSON.stringify(response.data.user));
                    
                    // Redirigir según el rol del usuario
                    const userRole = response.data.user.role;
                    if (userRole === 'admin') {
                        navigate('/admin');
                    } else if (userRole === 'lawyer') {
                        navigate('/abogado');
                    } else {
                        navigate('/cliente');
                    }
                } else {
                    console.error("La respuesta no contiene datos de usuario");
                    setError("Error: La respuesta del servidor no incluye datos de usuario");
                }
            } else {
                console.error("La respuesta no contiene token de acceso");
                setError("Error: La respuesta del servidor no incluye token de acceso");
            }
        } catch (err) {
            console.error('Error de login:', err);
            
            if (err.response) {
                // El servidor respondió con un código de estado diferente de 2xx
                if (err.response.status === 401) {
                    setError(err.response.data.detail || 'Credenciales incorrectas');
                } else if (err.response.status === 404) {
                    setError(`Servicio de autenticación no disponible en ${BACKEND_URL}/api/auth/login`);
                } else {
                    setError(`Error HTTP ${err.response.status}: ${err.response.data.detail || 'Hubo un problema al iniciar sesión'}`);
                }
            } else if (err.request) {
                // La solicitud fue hecha pero no se recibió respuesta
                setError(`No se pudo contactar al servidor en ${BACKEND_URL}. Verifica tu conexión y la URL del backend.`);
            } else {
                // Algo ocurrió al configurar la solicitud
                setError('Error al procesar la solicitud de inicio de sesión: ' + err.message);
            }
        } finally {
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
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
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
                    >
                        {showDebug ? 'Ocultar información técnica' : 'Mostrar información técnica'}
                    </button>
                </div>

                {showDebug && (
                    <div className="mt-4 p-4 border rounded-md bg-gray-50">
                        <h3 className="text-sm font-medium text-gray-800">Información de depuración:</h3>
                        <p className="text-xs mt-1">Backend URL: {BACKEND_URL}</p>
                        <p className="text-xs mt-1">Endpoint: {`${BACKEND_URL}/api/auth/login`}</p>
                        <div className="mt-2">
                            <button 
                                onClick={() => window.testLogin && window.testLogin(email, password)}
                                className="text-xs px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                                disabled={!email || !password || !window.testLogin}
                            >
                                Ejecutar prueba de login
                            </button>
                        </div>
                        <p className="text-xs mt-2 text-gray-500">
                            Revisa la consola del navegador para ver los resultados de la prueba.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoginForm; 