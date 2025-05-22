import React, { useState, useEffect } from 'react';
import apiClient, { endpoints } from '../api/apiClient';

const UsuariosDashboard = () => {
    const [usuarios, setUsuarios] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const cargarUsuarios = async () => {
            try {
                setCargando(true);
                // Esta es una página provisional - en una implementación real 
                // se conectaría con el endpoint real de usuarios
                
                // Simular carga de datos
                setTimeout(() => {
                    setUsuarios([
                        { id: 1, nombre: 'Admin Usuario', email: 'admin@example.com', rol: 'admin', activo: true },
                        { id: 2, nombre: 'Abogado Ejemplo', email: 'abogado@example.com', rol: 'abogado', activo: true },
                        { id: 3, nombre: 'Cliente Test', email: 'cliente@example.com', rol: 'cliente', activo: true },
                    ]);
                    setCargando(false);
                }, 1000);
            } catch (err) {
                console.error('Error al cargar usuarios:', err);
                setError('Error al cargar la lista de usuarios');
                setCargando(false);
            }
        };

        cargarUsuarios();
    }, []);

    if (cargando) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600">{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="mt-2 px-4 py-2 text-sm text-red-600 hover:text-red-800"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-6">Gestión de Usuarios</h1>
            
            <div className="mb-6">
                <p className="text-gray-600 mb-4">
                    Esta es una página provisional para gestionar usuarios. En la implementación final,
                    aquí podrás ver y administrar todos los usuarios del sistema.
                </p>
            </div>
            
            <div className="overflow-x-auto bg-white shadow-md rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                ID
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Nombre
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Email
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Rol
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Estado
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Acciones
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {usuarios.map((usuario) => (
                            <tr key={usuario.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {usuario.id}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {usuario.nombre}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {usuario.email}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                        usuario.rol === 'admin' ? 'bg-purple-100 text-purple-800' : 
                                        usuario.rol === 'abogado' ? 'bg-blue-100 text-blue-800' : 
                                        'bg-green-100 text-green-800'
                                    }`}>
                                        {usuario.rol}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                        usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                    }`}>
                                        {usuario.activo ? 'Activo' : 'Inactivo'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <button className="text-indigo-600 hover:text-indigo-900 mr-3">
                                        Editar
                                    </button>
                                    <button className="text-red-600 hover:text-red-900">
                                        {usuario.activo ? 'Desactivar' : 'Activar'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default UsuariosDashboard; 