import React from 'react';
import { useNavigate, NavLink } from 'react-router-dom';

const AdminNavbar = ({ user, onLogout }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Llamar al callback de logout proporcionado por el componente padre
        if (onLogout) {
            onLogout();
        }
        // Navegar explícitamente a la página de login
        navigate('/login', { replace: true });
    };
    
    // Función para navegar usando rutas relativas
    const navigateTo = (route) => {
        console.log(`[AdminNavbar] Navegando a ruta relativa: ${route}`);
        navigate(route);
    };

    return (
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
                            <NavLink
                                to="metricas"
                                className={({ isActive }) =>
                                    isActive
                                        ? "border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                }
                            >
                                Métricas
                            </NavLink>
                            <NavLink
                                to="usuarios"
                                className={({ isActive }) =>
                                    isActive
                                        ? "border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                }
                            >
                                Usuarios
                            </NavLink>
                            <NavLink
                                to="analytics"
                                className={({ isActive }) =>
                                    isActive
                                        ? "border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                }
                            >
                                Analytics
                            </NavLink>
                        </div>
                    </div>
                    <div className="hidden sm:ml-6 sm:flex sm:items-center">
                        <div className="ml-3 relative">
                            <div className="flex items-center">
                                <span className="text-sm text-gray-700 mr-4">
                                    {user ? `Hola, ${user.nombre || user.email}` : 'Admin'}
                                </span>
                                <button
                                    onClick={handleLogout}
                                    className="bg-red-600 text-white px-3 py-1 rounded-md text-sm hover:bg-red-700"
                                >
                                    Cerrar sesión
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default AdminNavbar; 