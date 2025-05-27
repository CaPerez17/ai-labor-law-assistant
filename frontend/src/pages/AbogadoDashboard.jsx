import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/apiClient';

const AbogadoDashboard = () => {
    const [casos, setCasos] = useState([]);
    const [casoSeleccionado, setCasoSeleccionado] = useState(null);
    const [filtroEstado, setFiltroEstado] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [metricas, setMetricas] = useState(null);
    const navigate = useNavigate();

    // Estados para chat y documentos
    const [mensajes, setMensajes] = useState([]);
    const [nuevoMensaje, setNuevoMensaje] = useState('');
    const [documentos, setDocumentos] = useState([]);

    useEffect(() => {
        cargarDatos();
    }, [filtroEstado]);

    const cargarDatos = async () => {
        try {
            setLoading(true);
            setError('');

            // Cargar casos del abogado
            await cargarCasos();
            
            // Cargar métricas
            await cargarMetricas();

        } catch (err) {
            console.error('Error cargando datos:', err);
            setError('Error al cargar los datos. Por favor, intente más tarde.');
        } finally {
            setLoading(false);
        }
    };

    const cargarCasos = async () => {
        try {
            const token = localStorage.getItem('token');
            let url = '/api/v1/abogado/casos';
            
            if (filtroEstado) {
                url += `?estado=${filtroEstado}`;
            }

            const response = await apiClient.get(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            setCasos(response.data || []);
        } catch (err) {
            console.error('Error cargando casos:', err);
            if (err.response?.status === 404) {
                setCasos([]); // Si no hay casos, mostrar lista vacía
            } else {
                throw err;
            }
        }
    };

    const cargarMetricas = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await apiClient.get('/api/v1/abogado/metricas', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            setMetricas(response.data);
        } catch (err) {
            console.error('Error cargando métricas:', err);
            // No lanzar error para que no interrumpa la carga de casos
        }
    };

    const seleccionarCaso = async (caso) => {
        setCasoSeleccionado(caso);
        
        // Cargar documentos del caso
        if (caso.id) {
            try {
                const token = localStorage.getItem('token');
                const response = await apiClient.get(`/api/v1/docs/caso/${caso.id}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setDocumentos(response.data || []);
            } catch (err) {
                console.error('Error cargando documentos:', err);
                setDocumentos([]);
            }
        }
    };

    const actualizarEstadoCaso = async (casoId, nuevoEstado, comentarios = '') => {
        try {
            const token = localStorage.getItem('token');
            await apiClient.put(`/api/v1/abogado/casos/${casoId}`, {
                estado: nuevoEstado,
                comentarios: comentarios
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            // Recargar casos
            await cargarCasos();
            
            // Actualizar caso seleccionado si es el mismo
            if (casoSeleccionado && casoSeleccionado.id === casoId) {
                const casoActualizado = casos.find(c => c.id === casoId);
                if (casoActualizado) {
                    setCasoSeleccionado({...casoActualizado, estado: nuevoEstado, comentarios});
                }
            }

            alert('Estado del caso actualizado exitosamente');
        } catch (err) {
            console.error('Error actualizando caso:', err);
            alert('Error al actualizar el estado del caso');
        }
    };

    const verificarCaso = async (casoId) => {
        await actualizarEstadoCaso(casoId, 'verificado', 'Caso verificado por el abogado');
    };

    const subirDocumento = async (event) => {
        const file = event.target.files[0];
        if (!file || !casoSeleccionado) return;

        try {
            const token = localStorage.getItem('token');
            const formData = new FormData();
            formData.append('file', file);
            formData.append('caso_id', casoSeleccionado.id.toString());
            formData.append('categoria', 'documento_caso');
            formData.append('subcategoria', 'evidencia');

            await apiClient.post('/api/v1/docs/upload', formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            // Recargar documentos
            seleccionarCaso(casoSeleccionado);
            alert('Documento subido exitosamente');
        } catch (err) {
            console.error('Error subiendo documento:', err);
            alert('Error al subir el documento');
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login', { replace: true });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Cargando dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Dashboard Abogado</h1>
                            <p className="text-gray-600">Gestiona tus casos y consultas legales</p>
                        </div>
                        <button
                            onClick={logout}
                            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                        >
                            Cerrar Sesión
                        </button>
                    </div>
                </div>
            </header>

            {error && (
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="bg-red-50 border border-red-200 rounded-md p-4">
                        <p className="text-red-800">{error}</p>
                    </div>
                </div>
            )}

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Métricas */}
                {metricas && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="text-2xl text-blue-600">📋</div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Total Casos
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {metricas.total_casos}
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="text-2xl text-yellow-600">⏳</div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Pendientes
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {metricas.casos_pendientes}
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="text-2xl text-green-600">✅</div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Resueltos
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {metricas.casos_resueltos}
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="text-2xl text-purple-600">📈</div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Tasa Resolución
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {metricas.tasa_resolucion.toFixed(1)}%
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Lista de Casos */}
                    <div className="lg:col-span-2">
                        <div className="bg-white shadow overflow-hidden sm:rounded-md">
                            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                                        Mis Casos ({casos.length})
                                    </h3>
                                    <select
                                        value={filtroEstado}
                                        onChange={(e) => setFiltroEstado(e.target.value)}
                                        className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                                    >
                                        <option value="">Todos los estados</option>
                                        <option value="pendiente">Pendientes</option>
                                        <option value="en_proceso">En proceso</option>
                                        <option value="pendiente_verificacion">Pendiente verificación</option>
                                        <option value="verificado">Verificados</option>
                                        <option value="resuelto">Resueltos</option>
                                        <option value="cerrado">Cerrados</option>
                                    </select>
                                </div>
                            </div>
                            <ul className="divide-y divide-gray-200">
                                {casos.length === 0 ? (
                                    <li className="px-4 py-4 text-gray-500 text-center">
                                        No hay casos para mostrar
                                    </li>
                                ) : (
                                    casos.map((caso) => (
                                        <li key={caso.id} className="px-4 py-4 hover:bg-gray-50">
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center justify-between">
                                                        <p className="text-sm font-medium text-indigo-600 truncate">
                                                            {caso.titulo}
                                                        </p>
                                                        <div className="ml-2 flex-shrink-0 flex">
                                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                                caso.estado === 'pendiente_verificacion' ? 'bg-yellow-100 text-yellow-800' :
                                                                caso.estado === 'verificado' ? 'bg-green-100 text-green-800' :
                                                                caso.estado === 'en_proceso' ? 'bg-blue-100 text-blue-800' :
                                                                caso.estado === 'resuelto' ? 'bg-green-100 text-green-800' :
                                                                'bg-gray-100 text-gray-800'
                                                            }`}>
                                                                {caso.estado.replace('_', ' ')}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <p className="mt-1 text-sm text-gray-600 truncate">
                                                        {caso.descripcion}
                                                    </p>
                                                    <div className="mt-2 flex items-center space-x-4">
                                                        <button
                                                            onClick={() => seleccionarCaso(caso)}
                                                            className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                                                        >
                                                            Ver detalles
                                                        </button>
                                                        {caso.estado === 'pendiente_verificacion' && (
                                                            <button
                                                                onClick={() => verificarCaso(caso.id)}
                                                                className="text-green-600 hover:text-green-900 text-sm font-medium"
                                                            >
                                                                ✅ Verificar caso
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        </li>
                                    ))
                                )}
                            </ul>
                        </div>
                    </div>

                    {/* Panel de detalles del caso */}
                    <div className="lg:col-span-1">
                        {casoSeleccionado ? (
                            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                                <div className="px-4 py-5 sm:px-6">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                                        Detalle del Caso
                                    </h3>
                                    <p className="mt-1 max-w-2xl text-sm text-gray-500">
                                        Información completa del caso seleccionado
                                    </p>
                                </div>
                                <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                                    <dl className="sm:divide-y sm:divide-gray-200">
                                        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                            <dt className="text-sm font-medium text-gray-500">Título</dt>
                                            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                                {casoSeleccionado.titulo}
                                            </dd>
                                        </div>
                                        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                            <dt className="text-sm font-medium text-gray-500">Estado</dt>
                                            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                    casoSeleccionado.estado === 'pendiente_verificacion' ? 'bg-yellow-100 text-yellow-800' :
                                                    casoSeleccionado.estado === 'verificado' ? 'bg-green-100 text-green-800' :
                                                    casoSeleccionado.estado === 'en_proceso' ? 'bg-blue-100 text-blue-800' :
                                                    casoSeleccionado.estado === 'resuelto' ? 'bg-green-100 text-green-800' :
                                                    'bg-gray-100 text-gray-800'
                                                }`}>
                                                    {casoSeleccionado.estado.replace('_', ' ')}
                                                </span>
                                            </dd>
                                        </div>
                                        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                            <dt className="text-sm font-medium text-gray-500">Descripción</dt>
                                            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                                {casoSeleccionado.descripcion}
                                            </dd>
                                        </div>
                                        {casoSeleccionado.comentarios && (
                                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                                <dt className="text-sm font-medium text-gray-500">Comentarios</dt>
                                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                                    {casoSeleccionado.comentarios}
                                                </dd>
                                            </div>
                                        )}
                                        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                            <dt className="text-sm font-medium text-gray-500">Documentos</dt>
                                            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                                <div className="space-y-2">
                                                    {documentos.length === 0 ? (
                                                        <p className="text-gray-500">No hay documentos</p>
                                                    ) : (
                                                        documentos.map((doc) => (
                                                            <div key={doc.id} className="flex items-center space-x-2">
                                                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                                                    {doc.nombre}
                                                                </span>
                                                            </div>
                                                        ))
                                                    )}
                                                    <div className="mt-2">
                                                        <input
                                                            type="file"
                                                            onChange={subirDocumento}
                                                            className="text-xs"
                                                        />
                                                    </div>
                                                </div>
                                            </dd>
                                        </div>
                                    </dl>
                                </div>

                                {/* Acciones del caso */}
                                <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                                    <select
                                        onChange={(e) => {
                                            if (e.target.value) {
                                                actualizarEstadoCaso(casoSeleccionado.id, e.target.value);
                                                e.target.value = '';
                                            }
                                        }}
                                        className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        <option value="">Cambiar estado</option>
                                        <option value="en_proceso">En proceso</option>
                                        <option value="verificado">Verificado</option>
                                        <option value="resuelto">Resuelto</option>
                                        <option value="cerrado">Cerrado</option>
                                    </select>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6 text-center text-gray-500">
                                Selecciona un caso para ver sus detalles
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AbogadoDashboard; 