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
        console.log('🔥 handleSubmit fired →', { email, password });
        setLoading(true);
        setError('');
        try {
            const { token, user } = await loginUser(email, password);
            console.log('✅ Login exitoso:', { token, user });
            
            if (!user) {
                throw new Error('No se recibieron datos del usuario');
            }
            
            // Guardar el token en localStorage
            localStorage.setItem('token', token);
            // Guardar datos del usuario
            localStorage.setItem('user', JSON.stringify(user));
            
            // Redirigir según el rol
            if (user.rol === 'admin') {
                navigate('/admin/metricas');
            } else if (user.rol === 'abogado') {
                navigate('/abogado');
            } else if (user.rol === 'cliente') {
                navigate('/cliente');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            console.error('❌ Error en login:', err);
            setError(err.message || 'Error al iniciar sesión');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Iniciar sesión en LegalAssista
                    </h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="email" className="sr-only">
                                Correo electrónico
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Correo electrónico"
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">
                                Contraseña
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Contraseña"
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="rounded-md bg-red-50 p-4">
                            <div className="flex">
                                <div className="ml-3">
                                    <h3 className="text-sm font-medium text-red-800">{error}</h3>
                                </div>
                            </div>
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white ${
                                loading
                                    ? 'bg-indigo-400 cursor-not-allowed'
                                    : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                            }`}
                        >
                            {loading ? (
                                <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                                    <svg
                                        className="animate-spin h-5 w-5 text-white"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                    >
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        ></circle>
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        ></path>
                                    </svg>
                                </span>
                            ) : null}
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