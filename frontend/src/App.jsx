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

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Verificar si hay un usuario guardado
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const handleLogin = (userData) => {
        setUser(userData);
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
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
                                        {user.nombre}
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