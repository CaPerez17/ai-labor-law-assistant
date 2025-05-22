import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Outlet } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import RegistroForm from './components/RegistroForm';
import OnboardingAssistant from './components/OnboardingAssistant';
import DocumentoAnalyzer from './components/DocumentoAnalyzer';
import AbogadoDashboard from './components/AbogadoDashboard';
import MetricasDashboard from './components/MetricasDashboard';
import UsuariosDashboard from './components/UsuariosDashboard';
import FacturacionUsuario from './components/FacturacionUsuario';
import ActivacionCuenta from './components/ActivacionCuenta';
import RecuperacionPassword from './components/RecuperacionPassword';
import AdminAnalyticsDashboard from './components/AdminAnalyticsDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorScreen from './components/ErrorScreen';
import AdminLayout from './layouts/AdminLayout';

// Importar la configuración con URLs fijas
import { BACKEND_URL } from './config';

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
        // No necesitamos redireccionar aquí, ya que AdminNavbar se encargará de eso
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
            <ErrorScreen 
                message={error}
                buttonText="Volver a iniciar sesión"
                onRetry={() => {
                    handleLogout();
                    window.location.href = '/login';
                }}
            />
        );
    }

    return (
        <Router>
            <div className="min-h-screen bg-gray-100">
                {user && user.rol !== 'admin' && (
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
                        
                        {/* Rutas protegidas utilizando el componente ProtectedRoute */}
                        <Route
                            path="/cliente"
                            element={
                                <ProtectedRoute 
                                    user={user} 
                                    roles={['cliente']} 
                                    fallback={
                                        <Navigate to="/login" replace />
                                    }
                                >
                                    <OnboardingAssistant />
                                </ProtectedRoute>
                            }
                        />
                        
                        <Route
                            path="/documento"
                            element={
                                <ProtectedRoute 
                                    user={user} 
                                    roles={['cliente']} 
                                    fallback={
                                        <Navigate to="/login" replace />
                                    }
                                >
                                    <DocumentoAnalyzer />
                                </ProtectedRoute>
                            }
                        />
                        
                        <Route
                            path="/facturas"
                            element={
                                <ProtectedRoute 
                                    user={user} 
                                    roles={['cliente']} 
                                    fallback={
                                        <Navigate to="/login" replace />
                                    }
                                >
                                    <FacturacionUsuario />
                                </ProtectedRoute>
                            }
                        />
                        
                        <Route
                            path="/abogado"
                            element={
                                <ProtectedRoute 
                                    user={user} 
                                    roles={['abogado', 'lawyer']} 
                                    fallback={
                                        <Navigate to="/login" replace />
                                    }
                                >
                                    <AbogadoDashboard />
                                </ProtectedRoute>
                            }
                        />
                        
                        <Route
                            path="/admin/*"
                            element={
                                <ProtectedRoute 
                                    user={user} 
                                    roles={['admin']} 
                                    fallback={
                                        <Navigate to="/login" replace />
                                    }
                                >
                                    <AdminLayout user={user} onLogout={handleLogout} />
                                </ProtectedRoute>
                            }
                        />
                        
                        <Route
                            path="/"
                            element={
                                user ? (
                                    <Navigate to={
                                        user.rol === 'admin' ? '/admin' :
                                        user.rol === 'abogado' ? '/abogado' :
                                        '/cliente'
                                    } />
                                ) : (
                                    <Navigate to="/login" />
                                )
                            }
                        />
                        
                        {/* Ruta para cualquier otra URL que no exista */}
                        <Route
                            path="*"
                            element={
                                <Navigate to="/" />
                            }
                        />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App; 