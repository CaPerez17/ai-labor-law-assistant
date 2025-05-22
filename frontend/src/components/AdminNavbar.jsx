import React from 'react';
import { useNavigate } from 'react-router-dom';

const AdminNavbar = ({ user, onLogout }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Llamar al callback de logout proporcionado por el componente padre
        onLogout();
        // Navegar explícitamente a la página de login
        navigate('/login');
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
                            <button
                                onClick={() => navigate('/admin/metricas')}
                                className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                            >
                                Métricas
                            </button>
                            <button
                                onClick={() => navigate('/admin/usuarios')}
                                className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                            >
                                Usuarios
                            </button>
                            <button
                                onClick={() => navigate('/admin/analytics')}
                                className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                            >
                                Analytics
                            </button>
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
    );
};

export default AdminNavbar; 