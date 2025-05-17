import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import RegistroForm from './components/RegistroForm';
import OnboardingAssistant from './components/OnboardingAssistant';
import DocumentoAnalyzer from './components/DocumentoAnalyzer';
import AbogadoDashboard from './components/AbogadoDashboard';
import MetricasDashboard from './components/MetricasDashboard';
import FacturacionUsuario from './components/FacturacionUsuario';
import ActivacionCuenta from './components/ActivacionCuenta';
import RecuperacionPassword from './components/RecuperacionPassword';
import AdminAnalyticsDashboard from './components/AdminAnalyticsDashboard';
import PrivateRoute from './components/PrivateRoute';

// Importar la configuración con URLs fijas
import { BACKEND_URL } from './config_override';

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Verificar si hay un usuario guardado
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        
        console.log('[App] Comprobando autenticación...');
        console.log('[App] Token existe:', !!token);
        console.log('[App] User data existe:', !!storedUser);
        
        if (!token) {
            console.log('[App] No hay token, considerando al usuario como no autenticado');
            setLoading(false);
            return;
        }
        
        if (storedUser) {
            try {
                const parsedUser = JSON.parse(storedUser);
                console.log('[App] Datos de usuario parseados correctamente:', parsedUser);
                
                // Normalizar el rol para manejar diferentes formatos (rol/role)
                if (!parsedUser.rol && parsedUser.role) {
                    console.log('[App] Normalizando rol: role → rol');
                    parsedUser.rol = parsedUser.role;
                }
                
                // Verificar que el usuario tenga un rol válido
                if (!parsedUser.rol) {
                    console.error('[App] Error: Usuario sin rol definido');
                    setError('El usuario no tiene un rol asignado. Por favor, contacte al administrador.');
                    // Mantener al usuario como null para mostrar pantalla de error
                } else {
                    // Normalizar el rol a minúscula para comparaciones consistentes
                    parsedUser.rol = parsedUser.rol.toLowerCase();
                    console.log('[App] Rol del usuario normalizado:', parsedUser.rol);
                    setUser(parsedUser);
                }
            } catch (e) {
                console.error('[App] Error al parsear datos de usuario:', e);
                localStorage.removeItem('user'); // Limpiar datos corruptos
                localStorage.removeItem('token');
                setError('Error al cargar datos de usuario. Por favor, inicie sesión nuevamente.');
            }
        } else {
            console.log('[App] No hay datos de usuario a pesar de tener token');
            localStorage.removeItem('token'); // Si hay token pero no hay user, limpiar token
        }
        
        setLoading(false);
    }, []);

    const handleLogin = (userData) => {
        console.log('[App] Usuario ha iniciado sesión:', userData);
        
        // Normalizar el rol si es necesario
        if (!userData.rol && userData.role) {
            userData.rol = userData.role;
        }
        
        // Normalizar a minúscula
        if (userData.rol) {
            userData.rol = userData.rol.toLowerCase();
        }
        
        setUser(userData);
        setError(null); // Limpiar errores previos
    };

    const handleLogout = () => {
        console.log('[App] Usuario cerrando sesión');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setError(null);
    };

    const isAuthenticated = () => {
        return localStorage.getItem('token') !== null;
    };

    const getUserRole = () => {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                const userData = JSON.parse(userStr);
                // Intentar con ambos formatos de rol
                return userData.rol || userData.role || null;
            } catch (error) {
                console.error('[App] Error al parsear datos de usuario:', error);
                return null;
            }
        }
        return null;
    };

    // Mostrar pantalla de carga
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    // Mostrar pantalla de error si hay un problema con los datos de usuario
    if (error) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 px-4">
                <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
                    <svg className="h-12 w-12 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">Ha ocurrido un error</h2>
                    <p className="text-gray-600 mb-6">{error}</p>
                    <button
                        onClick={() => {
                            handleLogout();
                            window.location.href = '/login';
                        }}
                        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none"
                    >
                        Volver a iniciar sesión
                    </button>
                </div>
            </div>
        );
    }

    return (
        <Router>
            <div className="min-h-screen bg-gray-100">
                {user && (
                    <nav className="bg-white shadow-sm">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex justify-between h-16">
                                <div className="flex">
                                    <div className="flex-shrink-0 flex items-center">
                                        <h1 className="text-xl font-bold text-indigo-600">
                                            Asistente Legal AI
                                        </h1>
                                    </div>
                                    <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                                        {user.rol === 'cliente' && (
                                            <>
                                                <button
                                                    onClick={() => window.location.href = '/cliente'}
                                                    className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700"
                                                >
                                                    Inicio
                                                </button>
                                                <button
                                                    onClick={() => window.location.href = '/documento'}
                                                    className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700"
                                                >
                                                    Analizar Documento
                                                </button>
                                                <button
                                                    onClick={() => window.location.href = '/facturas'}
                                                    className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700"
                                                >
                                                    Mis Facturas
                                                </button>
                                            </>
                                        )}
                                        {user.rol === 'abogado' && (
                                            <button
                                                onClick={() => window.location.href = '/abogado'}
                                                className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700"
                                            >
                                                Dashboard
                                            </button>
                                        )}
                                        {user.rol === 'admin' && (
                                            <>
                                                <button
                                                    onClick={() => window.location.href = '/admin/metricas'}
                                                    className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700"
                                                >
                                                    Métricas
                                                </button>
                                                <button
                                                    onClick={() => window.location.href = '/admin/usuarios'}
                                                    className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700"
                                                >
                                                    Usuarios
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <span className="text-sm text-gray-500 mr-4">
                                        {user.nombre || user.name || user.email}
                                    </span>
                                    <button
                                        onClick={handleLogout}
                                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                                    >
                                        Cerrar Sesión
                                    </button>
                                </div>
                            </div>
                        </div>
                    </nav>
                )}

                <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                    <Routes>
                        <Route
                            path="/login"
                            element={!user ? <LoginForm onLoginSuccess={handleLogin} /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/registro"
                            element={!user ? <RegistroForm /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/cliente"
                            element={user?.rol === 'cliente' ? <OnboardingAssistant /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/documento"
                            element={user?.rol === 'cliente' ? <DocumentoAnalyzer /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/facturas"
                            element={user?.rol === 'cliente' ? <FacturacionUsuario /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/abogado"
                            element={user?.rol === 'abogado' ? <AbogadoDashboard /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/metricas"
                            element={user?.rol === 'admin' ? <MetricasDashboard /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/analytics"
                            element={
                                <PrivateRoute roles={['admin']}>
                                    <AdminAnalyticsDashboard />
                                </PrivateRoute>
                            }
                        />
                        <Route
                            path="/"
                            element={
                                user ? (
                                    <Navigate to={
                                        user.rol === 'admin' ? '/admin/metricas' :
                                        user.rol === 'abogado' ? '/abogado' :
                                        '/cliente'
                                    } />
                                ) : (
                                    <Navigate to="/login" />
                                )
                            }
                        />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App; 